import streamlit as st
from src.db_tools.resume_db import create_resume_table
from src.db_tools.task_db import create_tasks_table
from src.db_tools.agent_db import create_agents_table
from src.db_tools.delegated_task_db import create_delegated_tasks_table

create_resume_table()
create_tasks_table()
create_agents_table()
create_delegated_tasks_table()

st.set_page_config(layout="wide") # Use wide layout for better space utilization

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Dashboard", "Add Member", "Add Task", "Add Agent", "Task Delegate"])

from views import add_member, add_task, add_agent, dashboard, task_delegate

# --- Main Content Area ---

if selection == "Dashboard":
    dashboard.render()
elif selection == "Add Member":
    add_member.render()
elif selection == "Add Task":
    add_task.render()
elif selection == "Add Agent":
    add_agent.render()
elif selection == "Task Delegate":
    task_delegate.render()
