import streamlit as st
from src.llm_tools.task_formatting import task_formatting
from src.db_tools.task_db import insert_task_data, create_tasks_table
from src.llm_tools.formatting import retry
def render():
    st.header("➕ Add New Task")
    st.write("Define a new task for the team by providing a detailed description.")

    with st.form("task_form", clear_on_submit=True):
        st.subheader("Task Details")
        task_deepflow_id = st.text_input("Deepflow Id", help="Enter the deepflow id of the task.")
        
        task_description = st.text_area("Task Description", height=200, help="Describe the task in detail. Include what needs to be done, the expected outcome, and any relevant context.")
        
        submit_button = st.form_submit_button("Analyze and Create Task")

        if submit_button:
            if task_description:
                with st.spinner("Analyzing task description..."):
                    task_data = retry(task_formatting,10,task_description)
                
                if task_data:
                    st.success("**Task analysis complete!**")
                    st.json(task_data)
                    try:
                        insert_task_data(task_deepflow_id, task_data)
                        st.success("Task data has been successfully stored in the database.")
                    except:
                        create_tasks_table()
                        insert_task_data(task_deepflow_id,task_data)
                        st.success("Task data has been successfully stored in the database.")
                else:
                    st.error("Failed to process the task description. Please try again or rephrase your description.")
            
            else:
                st.error("Please provide a task description.")
