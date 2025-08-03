import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field
import openai
from src.db_tools.connection_op import get_db_connection
from src.models import TaskData

# --- OpenAI Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. Embedding generation will fail.")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_openai_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """
    Generates a vector embedding for the given text using OpenAI's embedding model.
    """
    if not OPENAI_API_KEY:
        print("Error: OpenAI API key is not set. Cannot generate embeddings.")
        return []
    try:
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except openai.APIError as e:
        print(f"OpenAI API error during embedding generation: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during embedding generation: {e}")
        return []

def create_tasks_table():
    """
    Creates the 'tasks' table in the database if it doesn't already exist.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            deepflow_task_id TEXT NOT NULL,
            required_skills JSONB NOT NULL,
            sector TEXT,
            tags JSONB NOT NULL,
            manpower_needed INTEGER NOT NULL,
            roles_required JSONB NOT NULL,
            estimated_time INTEGER NOT NULL,
            embedding VECTOR(1536),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print(" 'tasks' table created or already exists.")

def insert_task_data(deepflow_task_id: str,task_data: TaskData):
    """
    Inserts a TaskData object into the 'tasks' table.
    """
    text_to_embed = (
        " ".join(task_data.required_skills) + " " +
        (task_data.sector if task_data.sector else "") + " " +
        " ".join(task_data.tags) + " " +
        " ".join(task_data.roles_required)
    ).strip()

    embedding = get_openai_embedding(text_to_embed)
    embedding_str = f"[{','.join(map(str, embedding))}]" if embedding else None

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (
            deepflow_task_id,
            required_skills,
            sector,
            tags,
            manpower_needed,
            roles_required,
            estimated_time,
            embedding
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        deepflow_task_id,
        json.dumps(task_data.required_skills),
        task_data.sector,
        json.dumps(task_data.tags),
        task_data.manpower_needed,
        json.dumps(task_data.roles_required),
        task_data.estimated_time,
        embedding_str
    ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Task with estimated time {task_data.estimated_time} hours inserted successfully.")

def get_all_tasks():
    """
    Retrieves all records from the 'tasks' table.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks;")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return tasks

def get_task_by_id(task_id: int):
    """
    Retrieves a single task from the 'tasks' table by its id.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()
    return task

if __name__ == '__main__':
    create_tasks_table()
