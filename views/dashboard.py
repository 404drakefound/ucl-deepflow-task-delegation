import streamlit as st
import pandas as pd
from src.db_tools.resume_db import get_all_resumes
from src.db_tools.task_db import get_all_tasks
from src.db_tools.agent_db import get_all_agents
from src.db_tools.delegated_task_db import get_all_delegated_tasks

def render():
    st.header("📊 Dashboard")

    # --- Delegated Tasks ---
    with st.expander("📋 All Delegated Tasks"):
        delegated_tasks = get_all_delegated_tasks()
        if delegated_tasks:
            df_delegated_tasks = pd.DataFrame(delegated_tasks, columns=['Task ID', 'Member IDs', 'Agent IDs', 'Created At', 'Updated At'])
            st.dataframe(df_delegated_tasks)
        else:
            st.write("No delegated tasks found.")

    # --- Members ---
    with st.expander("👥 All Members"):
        members = get_all_resumes()
        if members:
            df_members = pd.DataFrame(members, columns=['ID', 'Deepflow ID', 'Personal Summary', 'Technical Skills', 'Certifications', 'Soft Skills', 'Vocal Attributes', 'Task Delegation Recommendations', 'Specialization Task Categories', 'Additional Observations', 'Embedding', 'Created At'])
            st.dataframe(df_members)
        else:
            st.write("No members found.")

    # --- Tasks ---
    with st.expander("📝 All Tasks"):
        tasks = get_all_tasks()
        if tasks:
            df_tasks = pd.DataFrame(tasks, columns=['ID', 'Deepflow ID', 'Required Skills', 'Sector', 'Tags', 'Manpower Needed', 'Roles Required', 'Estimated Time', 'Embedding', 'Created At'])
            st.dataframe(df_tasks)
        else:
            st.write("No tasks found.")

    # --- Agents ---
    with st.expander("🤖 All Agents"):
        agents = get_all_agents()
        if agents:
            df_agents = pd.DataFrame(agents, columns=['ID', 'Deepflow ID', 'Tags', 'Skills', 'Capabilities', 'Core Functionalities', 'Embedding', 'Created At'])
            st.dataframe(df_agents)
        else:
            st.write("No agents found.")
