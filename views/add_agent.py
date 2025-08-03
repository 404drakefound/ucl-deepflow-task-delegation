import streamlit as st
from src.llm_tools.agent_formatting import agent_formatting
from src.models import AgentData
from src.db_tools.agent_db import insert_agent_data, create_agents_table
from src.llm_tools.formatting import retry

def render():
    st.header("🤖 Add New Agent")
    st.write("Define a new agent for the team by providing a detailed description.")

    with st.form("agent_form", clear_on_submit=True):
        st.subheader("Agent Details")
        deepflow_agent_id = st.text_input("Deepflow Agent ID", help="Enter the unique Deepflow ID for this agent.")
        
        agent_description = st.text_area("Agent Description", height=200, help="Describe the agent in detail. Include what it does, its skills, and its core functions.")
        
        submit_button = st.form_submit_button("Analyze and Create Agent")

        if submit_button:
            if agent_description:
                with st.spinner("Analyzing agent description..."):
                    agent_data = retry(agent_formatting, 5, agent_description)
                
                if agent_data:
                    st.success("**Agent analysis complete!**")
                    st.json(agent_data.dict())
                    try:
                        insert_agent_data(deepflow_agent_id, agent_data)
                        st.success("Agent data has been successfully stored in the database.")
                    except:
                        create_agents_table()
                        insert_agent_data(deepflow_agent_id, agent_data)
                        st.success("Agent data has been successfully stored in the database.")
                else:
                    st.error("Failed to process the agent description. Please try again or rephrase your description.")
            
            else:
                st.error("Please provide an agent description.")
