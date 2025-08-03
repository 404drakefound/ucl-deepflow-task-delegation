import json
import os
from typing import List
from pydantic import BaseModel, Field
import openai
from src.db_tools.connection_op import get_db_connection
from src.models import AgentData

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

def create_agents_table():
    """
    Creates the 'agents' table in the database if it doesn't already exist.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id SERIAL PRIMARY KEY,
            deepflow_agent_id TEXT NOT NULL,
            tags JSONB,
            skills JSONB,
            capabilities JSONB,
            core_functionalities JSONB,
            embedding VECTOR(1536),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print(" 'agents' table created or already exists.")

def insert_agent_data(deepflow_agent_id: str, agent_data: AgentData):
    """
    Inserts an AgentData object into the 'agents' table.
    """
    text_to_embed = (
        " ".join(agent_data.tags) + " " +
        " ".join(agent_data.skills) + " " +
        " ".join(agent_data.capabilities) + " " +
        " ".join(agent_data.core_functionalities)
    ).strip()

    embedding = get_openai_embedding(text_to_embed)
    embedding_str = f"[{','.join(map(str, embedding))}]" if embedding else None

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO agents (
            deepflow_agent_id,
            tags,
            skills,
            capabilities,
            core_functionalities,
            embedding
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        deepflow_agent_id,
        json.dumps(agent_data.tags),
        json.dumps(agent_data.skills),
        json.dumps(agent_data.capabilities),
        json.dumps(agent_data.core_functionalities),
        embedding_str
    ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Agent with ID {deepflow_agent_id} inserted successfully.")

def get_all_agents():
    """
    Retrieves all records from the 'agents' table.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agents;")
    agents = cur.fetchall()
    cur.close()
    conn.close()
    return agents

def find_similar_agents(task_embedding: List[float], top_n: int = 3):
    """
    Finds the top_n most similar agents to a given task embedding.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    embedding_str = f"[{','.join(map(str, task_embedding))}]"
    # Use the <=> operator for cosine distance
    cur.execute("""
        SELECT deepflow_agent_id, 1 - (embedding <=> %s) AS similarity
        FROM agents
        ORDER BY similarity DESC
        LIMIT %s;
    """, (embedding_str, top_n))
    similar_agents = cur.fetchall()
    cur.close()
    conn.close()
    return similar_agents

def get_agent_by_id(deepflow_agent_id: str):
    """
    Retrieves a single agent from the 'agents' table by its deepflow_agent_id.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agents WHERE deepflow_agent_id = %s;", (deepflow_agent_id,))
    agent = cur.fetchone()
    cur.close()
    conn.close()
    return agent

if __name__ == '__main__':
    create_agents_table()
