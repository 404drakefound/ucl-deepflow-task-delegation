import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")  # Load environment variables from .env file

def get_db_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URI"))
    return conn
