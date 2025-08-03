import os
from src.llm_tools.resume_formatting import upload_file_to_openai, resume_formatting
from src.db_tools.resume_db import insert_resume_data, create_resume_table
from src.llm_tools.formatting import retry

def create_members_from_resumes():
    resume_dir = "data/resume"
    pdf_files = [f for f in os.listdir(resume_dir) if f.endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in {resume_dir}")
        return

    # Ensure the resume table exists
    try:
        create_resume_table()
        print("Resume table checked/created successfully.")
    except Exception as e:
        print(f"Error checking/creating resume table: {e}")
        return

    for i, pdf_file in enumerate(pdf_files):
        file_path = os.path.join(resume_dir, pdf_file)
        member_deepflow_id = f"{os.path.splitext(pdf_file)[0]}{i}" # Generate a unique ID

        print(f"\nProcessing {pdf_file} for member ID: {member_deepflow_id}")
        try:
            with open(file_path, "rb") as file:
                file_id = upload_file_to_openai(file)
            
            if file_id:
                print(f"File {pdf_file} uploaded to OpenAI with ID: {file_id}")
                
                # Call resume_formatting (note: it doesn't use file_id to retrieve content based on current implementation)
                output = retry(resume_formatting, 5, file_id)
                
                if output:
                    print(f"Resume formatting successful for {pdf_file}.")
                    # Assuming output is a Pydantic model or dict that can be directly inserted
                    insert_resume_data(member_deepflow_id, output)
                    print(f"Resume data for {member_deepflow_id} stored in database.")
                else:
                    print(f"Failed to format resume for {pdf_file}.")
            else:
                print(f"Failed to upload {pdf_file} to OpenAI.")
        except Exception as e:
            print(f"An error occurred while processing {pdf_file}: {e}")

if __name__ == "__main__":
    create_members_from_resumes()
