import json
from src.db_tools.connection_op import get_db_connection
from typing import List

def create_delegated_tasks_table():
    """
    Creates the 'delegated_tasks' table in the database if it doesn't already exist.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS delegated_tasks (
            task_id INTEGER PRIMARY KEY,
            member_ids TEXT[],
            agent_ids TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        );
    """)
    # Add a trigger to update the updated_at column
    cur.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    cur.execute("""
        DROP TRIGGER IF EXISTS update_delegated_tasks_updated_at ON delegated_tasks;
        CREATE TRIGGER update_delegated_tasks_updated_at
        BEFORE UPDATE ON delegated_tasks
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    conn.commit()
    cur.close()
    conn.close()
    print(" 'delegated_tasks' table created or already exists.")

def insert_delegated_task(task_id: int, member_ids: List[str], agent_ids: List[str]):
    """
    Inserts or updates a delegated task record in the 'delegated_tasks' table.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO delegated_tasks (task_id, member_ids, agent_ids)
        VALUES (%s, %s, %s)
        ON CONFLICT (task_id) DO UPDATE SET
            member_ids = EXCLUDED.member_ids,
            agent_ids = EXCLUDED.agent_ids;
    """, (task_id, member_ids, agent_ids))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Delegated task for task ID {task_id} inserted or updated successfully.")

def get_all_delegated_tasks():
    """
    Retrieves all records from the 'delegated_tasks' table.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM delegated_tasks;")
    delegated_tasks = cur.fetchall()
    cur.close()
    conn.close()
    return delegated_tasks

if __name__ == '__main__':
    create_delegated_tasks_table()
