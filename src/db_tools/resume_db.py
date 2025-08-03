import json
import os
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from src.models import ResumeData
# Ensure you have the 'openai' library installed: pip install openai
import openai

# Assuming src.db_tools.connection_op.get_db_connection is correctly set up
# This function should return a psycopg2 connection object.
from src.db_tools.connection_op import get_db_connection

# --- OpenAI Configuration ---
# It's highly recommended to load your API key from environment variables
# For example: export OPENAI_API_KEY='your_api_key_here'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. Embedding generation will fail.")
    # You might want to raise an error or handle this more robustly in a production environment
    # raise ValueError("OPENAI_API_KEY environment variable not set.")

# Initialize OpenAI client (ensure you have the 'openai' package installed)
# For older versions of openai library, you might use: openai.api_key = OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- Embedding Generation Function ---
def get_openai_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """
    Generates a vector embedding for the given text using OpenAI's embedding model.

    Args:
        text (str): The input text to embed.
        model (str): The OpenAI embedding model to use. Default is "text-embedding-ada-002".

    Returns:
        List[float]: A list of floats representing the vector embedding.
                     Returns an empty list if embedding generation fails.
    """
    if not OPENAI_API_KEY:
        print("Error: OpenAI API key is not set. Cannot generate embeddings.")
        return []
    try:
        # OpenAI's embedding API expects a list of strings, even for a single text
        response = client.embeddings.create(input=[text], model=model)
        # The embedding is in response.data[0].embedding
        return response.data[0].embedding
    except openai.APIError as e:
        print(f"OpenAI API error during embedding generation: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during embedding generation: {e}")
        return []

# --- Database Table Creation Function ---
def create_resume_table():
    """
    Creates the 'resumes' table in the database if it doesn't already exist,
    including a 'vector' column for storing embeddings and 'deepflow_member_id'.
    Requires the pgvector extension to be enabled in your PostgreSQL database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check if pgvector extension is enabled (optional, but good practice)
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        print("pgvector extension ensured.")

        # Create the resumes table with a VECTOR column and deepflow_member_id
        # text-embedding-ada-002 produces 1536-dimensional vectors
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id SERIAL PRIMARY KEY,
                deepflow_member_id TEXT UNIQUE NOT NULL, -- New column for Deepflow Member ID
                personal_summary TEXT NOT NULL,
                technical_skills JSONB NOT NULL,
                certifications JSONB NOT NULL,
                soft_skills JSONB NOT NULL,
                vocal_attributes TEXT,
                task_delegation_recommendations JSONB NOT NULL,
                specialization_task_categories JSONB NOT NULL,
                additional_observations JSONB NOT NULL,
                embedding VECTOR(1536), -- New column for storing the vector embedding
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print(" 'resumes' table created or already exists with 'embedding' and 'deepflow_member_id' columns.")
    except Exception as e:
        print(f"Error creating resumes table: {e}")
        conn.rollback() # Rollback in case of error
    finally:
        cur.close()
        conn.close()

# --- Data Insertion Function (Modified) ---
def insert_resume_data(deepflow_member_id, resume_data: ResumeData):
    """
    Inserts a ResumeData object into the 'resumes' table,
    generating and storing its vector embedding, including deepflow_member_id.

    Args:
        resume_data: An instance of the ResumeData Pydantic model.
    """
    # Concatenate relevant text fields for embedding generation
    text_to_embed = (
        resume_data.personal_summary + " " +
        " ".join(resume_data.technical_skills) + " " +
        " ".join(resume_data.soft_skills) + " " +
        " ".join(resume_data.certifications) + " " +
        " ".join(resume_data.task_delegation_recommendations) + " " +
        " ".join(resume_data.specialization_task_categories) + " " +
        " ".join(resume_data.additional_observations)
    ).strip()

    # Generate the embedding
    embedding = get_openai_embedding(text_to_embed)

    if not embedding:
        print("Warning: Could not generate embedding for resume. Storing without embedding.")
        # If embedding fails, store None or an empty vector, depending on your schema's NULLability
        embedding_str = None
    else:
        # Convert the list of floats to a string representation for PostgreSQL's VECTOR type
        # pgvector expects '[val1, val2, ...]' format
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO resumes (
                deepflow_member_id, -- New column
                personal_summary,
                technical_skills,
                certifications,
                soft_skills,
                vocal_attributes,
                task_delegation_recommendations,
                specialization_task_categories,
                additional_observations,
                embedding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            deepflow_member_id, # Pass the deepflow_member_id
            resume_data.personal_summary,
            json.dumps(resume_data.technical_skills),
            json.dumps(resume_data.certifications),
            json.dumps(resume_data.soft_skills),
            resume_data.vocal_attributes,
            json.dumps(resume_data.task_delegation_recommendations),
            json.dumps(resume_data.specialization_task_categories),
            json.dumps(resume_data.additional_observations),
            embedding_str
        ))
        conn.commit()
        print(f"Resume data for member ID '{deepflow_member_id}' inserted successfully. Embedding {'generated and stored' if embedding else 'failed to generate'}.")
    except Exception as e:
        print(f"Error inserting resume data for member ID '{deepflow_member_id}': {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_all_resumes():
    """
    Retrieves all records from the 'resumes' table.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resumes;")
    resumes = cur.fetchall()
    cur.close()
    conn.close()
    return resumes

def find_similar_resumes(task_embedding: List[float], top_n: int = 3):
    """
    Finds the top_n most similar resumes to a given task embedding.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    embedding_str = f"[{','.join(map(str, task_embedding))}]"
    # Use the <=> operator for cosine distance
    cur.execute("""
        SELECT deepflow_member_id, 1 - (embedding <=> %s) AS similarity
        FROM resumes
        ORDER BY similarity DESC
        LIMIT %s;
    """, (embedding_str, top_n))
    similar_resumes = cur.fetchall()
    cur.close()
    conn.close()
    return similar_resumes

def get_resume_by_id(deepflow_member_id: str):
    """
    Retrieves a single resume from the 'resumes' table by its deepflow_member_id.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resumes WHERE deepflow_member_id = %s;", (deepflow_member_id,))
    resume = cur.fetchone()
    cur.close()
    conn.close()
    return resume

# --- Example Usage ---
if __name__ == '__main__':
    # Make sure your get_db_connection() function is correctly set up
    # to connect to your PostgreSQL database.

    # 1. Create the table (or ensure it exists with the embedding column)
    create_resume_table()

    # 2. Create a dummy ResumeData object with deepflow_member_id
    sample_resume = ResumeData(
        personal_summary="Highly motivated software engineer with expertise in Python and cloud technologies.",
        technical_skills=["Python", "Django", "SQL", "AWS", "Docker", "Kubernetes"],
        certifications=["AWS Certified Developer – Associate"],
        soft_skills=["Problem-solving", "Teamwork", "Communication", "Adaptability"],
        vocal_attributes="Clear and articulate.",
        task_delegation_recommendations=["Lead backend development tasks", "Mentor junior developers"],
        specialization_task_categories=["Backend Development", "Cloud Infrastructure", "API Design"],
        additional_observations=["Strong analytical skills.", "Excellent documentation habits."]
    )

    # 3. Insert the dummy resume data (this will now generate and store the embedding)
    insert_resume_data("DFM-001",sample_resume)

    # Example of another resume with a different deepflow_member_id
    sample_resume_2 = ResumeData(
        personal_summary="Experienced marketing professional with a focus on digital campaigns and content strategy.",
        technical_skills=["SEO", "SEM", "Google Analytics", "Content Management Systems"],
        certifications=["Google Ads Certification"],
        soft_skills=["Creativity", "Strategic Thinking", "Client Management"],
        vocal_attributes=None,
        task_delegation_recommendations=["Develop content calendars", "Manage social media campaigns"],
        specialization_task_categories=["Digital Marketing", "Content Strategy", "Brand Management"],
        additional_observations=["Proven track record of increasing engagement.", "Strong presentation skills."]
    )
    insert_resume_data("DFM-002",sample_resume_2)

    # Example of attempting to insert with a duplicate deepflow_member_id (will cause an error)
    # try:
    #     duplicate_resume = ResumeData(
    #         deepflow_member_id="DFM-001", # This will cause a unique constraint violation
    #         personal_summary="Another resume for DFM-001.",
    #         technical_skills=["JavaScript"],
    #         certifications=[],
    #         soft_skills=["Communication"],
    #         vocal_attributes=None,
    #         task_delegation_recommendations=[],
    #         specialization_task_categories=[],
    #         additional_observations=[]
    #     )
    #     insert_resume_data(duplicate_resume)
    # except Exception as e:
    #     print(f"\nCaught expected error for duplicate deepflow_member_id: {e}")
