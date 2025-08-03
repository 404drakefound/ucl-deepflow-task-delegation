import streamlit as st
import pandas as pd
from src.db_tools.task_db import get_all_tasks, get_task_by_id
from src.db_tools.resume_db import find_similar_resumes, get_resume_by_id
from src.db_tools.agent_db import find_similar_agents, get_agent_by_id
from src.llm_tools.delegation_formatting import delegate_task
from src.llm_tools.formatting import retry
import numpy as np
from src.db_tools.delegated_task_db import insert_delegated_task

def render():
    st.header("🤝 Task Delegate")

    tasks = get_all_tasks()
    
    if not tasks:
        st.warning("No tasks found. Please add a task first.")
        return

    task_options = {f"{task[1]} (ID: {task[0]})": task for task in tasks}
    selected_task_str = st.selectbox("Select a Task", options=list(task_options.keys()))

    if st.button("Delegate Task"):
        if selected_task_str:
            selected_task_id = int(selected_task_str.split('(ID: ')[1][:-1])
            selected_task = get_task_by_id(selected_task_id)

            if selected_task:
                task_embedding_str = selected_task[8]
                if task_embedding_str:
                    print("--- Task Delegate Debug ---")
                    print(f"Selected Task: {selected_task}")
                    task_embedding = [float(x) for x in task_embedding_str.strip('[]').split(',')]
                    # print(f"Task Embedding: {task_embedding[:5]}...") # Print first 5 elements

                    similar_members_data = find_similar_resumes(task_embedding)
                    # print(f"Similar Members: {similar_members_data}")
                    similar_agents_data = find_similar_agents(task_embedding)
                    # print(f"Similar Agents: {similar_agents_data}")

                    member_details = [get_resume_by_id(member[0]) for member in similar_members_data]
                    
                    # print(f"Member Details: {member_details}")
                    agent_details = [get_agent_by_id(agent[0]) for agent in similar_agents_data]
                    # print(f"Agent Details: {agent_details}")


                    task_cols = ['id', 'deepflow_task_id', 'required_skills', 'sector', 'tags', 'manpower_needed', 'roles_required', 'estimated_time', 'embedding', 'created_at']
                    member_cols = ['id', 'deepflow_member_id', 'personal_summary', 'technical_skills', 'certifications', 'soft_skills', 'vocal_attributes', 'task_delegation_recommendations', 'specialization_task_categories', 'additional_observations', 'embedding', 'created_at']
                    agent_cols = ['id', 'deepflow_agent_id', 'tags', 'skills', 'capabilities', 'core_functionalities', 'embedding', 'created_at']
                    print("got the best fit")
                    task_details_dict = dict(zip(task_cols, selected_task)) if selected_task else {}
                    # print(f"Task Details Dict: {task_details_dict}")
                    member_details_dicts = [dict(zip(member_cols, member)) for member in member_details if member]
                    # print(f"Member Details Dicts: {member_details_dicts}")
                    agent_details_dicts = [dict(zip(agent_cols, agent)) for agent in agent_details if agent]
                    # print(f"Agent Details Dicts: {agent_details_dicts}")

                    task_details_dict.pop('embedding')
                    for member in member_details_dicts:
                        member.pop('embedding')
                    for agent in agent_details_dicts:
                        agent.pop("embedding")

                    print("finding the best com")
                    with st.spinner("Finding the best combination..."):
                        delegation_result = retry(delegate_task, 3, task_details_dict, member_details_dicts, agent_details_dicts)
                    if delegation_result:
                        st.subheader("🏆 Best Combination for the Task")
                        st.write(delegation_result.reasoning)
                        st.json(delegation_result.best_combination)

                        # Extract member and agent IDs from the LLM response
                        member_ids = [key[7:] for key in delegation_result.best_combination.keys() if 'member'==key[:6]]
                        agent_ids = [key[6:] for key in delegation_result.best_combination.keys() if 'agent' in key[:5]]
                        
                        task_id = task_details_dict['id']
                        
                        try:
                            insert_delegated_task(task_id, member_ids, agent_ids)
                            st.success("Successfully saved the delegation record.")
                        except Exception as e:
                            st.error(f"Failed to save the delegation record: {e}")

                    else:
                        st.error("Could not determine the best combination. Please try again.")
                else:
                    st.error("The selected task does not have an embedding. Cannot perform semantic search.")
            else:
                st.error("Could not retrieve selected task details.")
