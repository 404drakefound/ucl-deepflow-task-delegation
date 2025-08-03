import os
from dotenv import load_dotenv
from src.llm_tools.resume_formatting import resume_formatting
from src.llm_tools.agent_formatting import agent_formatting
from src.llm_tools.task_formatting import task_formatting
from src.llm_tools.delegation_formatting import delegate_task
from src.db_tools.resume_db import insert_resume_data, get_resume_by_id, find_similar_resumes
from src.db_tools.agent_db import insert_agent_data, get_agent_by_id, find_similar_agents
from src.db_tools.task_db import insert_task_data, get_task_by_id, get_all_tasks
from src.db_tools.delegated_task_db import insert_delegated_task
from src.llm_tools.formatting import retry

# Load environment variables
load_dotenv()

def test_add_member(file_path: str, deepflow_member_id: str):
    """
    Reads a resume from a file, processes it, and stores it in the database.
    """
    print(f"--- Running Test: Add Member (ID: {deepflow_member_id}) ---")
    try:
        with open(file_path, 'r') as f:
            resume_text = f.read()
        
        print("Formatting resume...")
        resume_data = retry(resume_formatting, 5, resume_text)
        
        if resume_data:
            print("Inserting resume data into database...")
            insert_resume_data(deepflow_member_id, resume_data)
            print(f"✅ Test Add Member (ID: {deepflow_member_id}) PASSED")
        else:
            print("❌ Test Add Member FAILED: Could not format resume.")
            
    except FileNotFoundError:
        print(f"❌ Test Add Member FAILED: File not found at {file_path}")
    except Exception as e:
        print(f"❌ Test Add Member FAILED: An error occurred: {e}")
    print("-" * 20)

def test_add_agent(agent_description: str, deepflow_agent_id: str):
    """
    Processes an agent description and stores it in the database.
    """
    print(f"--- Running Test: Add Agent (ID: {deepflow_agent_id}) ---")
    try:
        print("Formatting agent description...")
        agent_data = retry(agent_formatting, 5, agent_description)
        
        if agent_data:
            print("Inserting agent data into database...")
            insert_agent_data(deepflow_agent_id, agent_data)
            print(f"✅ Test Add Agent (ID: {deepflow_agent_id}) PASSED")
        else:
            print("❌ Test Add Agent FAILED: Could not format agent description.")
            
    except Exception as e:
        print(f"❌ Test Add Agent FAILED: An error occurred: {e}")
    print("-" * 20)

def test_delegate_task(task_description: str, deepflow_task_id: str):
    """
    Creates a task, delegates it, and stores the delegation record.
    """
    print(f"--- Running Test: Delegate Task (ID: {deepflow_task_id}) ---")
    try:
        # 1. Create the task
        print("Formatting task description...")
        task_data = retry(task_formatting, 5, task_description)
        if not task_data:
            print("❌ Test Delegate Task FAILED: Could not format task description.")
            return
            
        print("Inserting task data into database...")
        insert_task_data(deepflow_task_id, task_data)
        
        # 2. Get the newly created task's ID and embedding
        # This is a simplification; in a real scenario, you'd query by deepflow_task_id
        tasks = get_all_tasks()
        new_task = tasks[-1]
        task_id = new_task[0]
        task_embedding_str = new_task[8]
        
        if not task_embedding_str:
            print("❌ Test Delegate Task FAILED: Task was created without an embedding.")
            return
            
        task_embedding = [float(x) for x in task_embedding_str.strip('[]').split(',')]

        # 3. Find similar members and agents
        print("Finding similar members and agents...")
        similar_members = find_similar_resumes(task_embedding)
        similar_agents = find_similar_agents(task_embedding)

        # 4. Get full details
        print("Fetching full details...")
        member_details = [get_resume_by_id(m[0]) for m in similar_members]
        agent_details = [get_agent_by_id(a[0]) for a in similar_agents]

        # 5. Convert to dicts
        task_cols = ['id', 'deepflow_task_id', 'required_skills', 'sector', 'tags', 'manpower_needed', 'roles_required', 'estimated_time', 'embedding', 'created_at']
        member_cols = ['id', 'deepflow_member_id', 'personal_summary', 'technical_skills', 'certifications', 'soft_skills', 'vocal_attributes', 'task_delegation_recommendations', 'specialization_task_categories', 'additional_observations', 'embedding', 'created_at']
        agent_cols = ['id', 'deepflow_agent_id', 'tags', 'skills', 'capabilities', 'core_functionalities', 'embedding', 'created_at']

        task_details_dict = dict(zip(task_cols, new_task))
        member_details_dicts = [dict(zip(member_cols, m)) for m in member_details if m]
        agent_details_dicts = [dict(zip(agent_cols, a)) for a in agent_details if a]
        task_details_dict.pop('embedding')
        for member in member_details_dicts:
            member.pop('embedding')
        for agent in agent_details_dicts:
            agent.pop('embedding')
        # 6. Get LLM recommendation
        print("Getting LLM recommendation...")
        delegation_result = retry(delegate_task, 3, task_details_dict, member_details_dicts, agent_details_dicts)

        if delegation_result:
            # 7. Store the result
            print("Storing delegation record...")
            member_ids = [key[7:] for key in delegation_result.best_combination.keys() if 'member'== key[0:6]]
            agent_ids = [key[6:] for key in delegation_result.best_combination.keys() if 'agent' == key[0:5]]
            insert_delegated_task(task_id, member_ids, agent_ids)
            print(f"✅ Test Delegate Task (ID: {deepflow_task_id}) PASSED")
        else:
            print("❌ Test Delegate Task FAILED: Could not get LLM recommendation.")

    except Exception as e:
        print(f"❌ Test Delegate Task FAILED: An error occurred: {e}")
    print("-" * 20)


if __name__ == '__main__':
    # To run this test, create a resume file e.g., 'data/resume/test_resume.txt'
    # and then call the function.
    # test_add_member('data/resume/test_resume.txt', 'DFM-TEST-001')
    pass
