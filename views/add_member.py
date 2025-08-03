import streamlit as st
from src.llm_tools.resume_formatting import upload_file_to_openai, resume_formatting
from src.db_tools.resume_db import insert_resume_data, create_resume_table
from src.llm_tools.formatting import retry
def render():
    st.header("👤 Add New Member")
    st.write("Please fill in the member's details and upload their resume.")

    with st.form("member_form", clear_on_submit=True):
        st.subheader("Member Details")
        member_name = st.text_input("Name", help="Enter the full name of the member.")
        member_deepflow_id = st.text_input("Deepflow Id", help="Enter the deepflow id of the member.")
        
        st.subheader("Resume Upload")
        uploaded_resume = st.file_uploader("Upload Resume (PDF, DOCX)", type=["pdf", "docx"], help="Upload the member's resume file.")

        submit_button = st.form_submit_button("Submit Member")

        if submit_button:
            if member_name and member_deepflow_id:
                st.success(f"**Successfully added new member: {member_name}!**")
                st.write(f"- **Deepflow ID:** {member_deepflow_id}")
                if uploaded_resume:
                    st.write(f"- **Resume Uploaded:** {uploaded_resume.name} (Type: {uploaded_resume.type}, Size: {uploaded_resume.size / 1024:.2f} KB)")
                    # In a real application, you'd save this file to storage
                else:
                    st.warning("No resume was uploaded.")
                
                file_id=upload_file_to_openai(uploaded_resume)

                output=retry(resume_formatting,5,file_id)
                if output:
                    st.json(output)
                    try:
                        insert_resume_data(member_deepflow_id,output)
                        st.success("Resume data has been successfully stored in the database.")
                    except:
                        create_resume_table()
                        insert_resume_data(member_deepflow_id,output)
                        st.success("Resume data has been successfully stored in the database.")

                else:
                    st.error("Failed to process the resume. Please try again.")
                st.info("You can integrate this with a backend to store data and resumes permanently.")
            else:
                st.error("Please fill in all required fields: Name, Deepflow ID.")
