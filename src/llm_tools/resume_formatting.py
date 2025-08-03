from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
# file to openai
from openai import OpenAI
load_dotenv(dotenv_path=".env")  # Load environment variables from .env file
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
# runnablelambda
from langchain_core.runnables import RunnableLambda
from typing import Dict, Any, List
import json
from openai.types.chat import ChatCompletionMessageParam

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

json_parser = JsonOutputParser()

from src.models import ResumeData
from pydantic import BaseModel, Field
from typing import List, Optional


def upload_file_to_openai(file):
    """
    Function to upload a file to OpenAI and return the file ID.
    """
    file_obj = client.files.create(file=file, purpose="user_data")
    file_id = file_obj.id
    print(f"File uploaded successfully. File ID: {file_id}")
    return file_id

def resume_formatting(file_id: str):
    """
    Test function to upload a file to OpenAI and return the file ID.
    """
    messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": [ {
                    "type": "file",
                    "file": {
                        "file_id": file_id,
                    }
                },                {
                    "type": "text",
                    "text":"You are a highly accurate resume parser. "
            "Fetch skills and other fields, by looking at there education, experiences and the overall resume, not just what they have mentioned,Your task is to extract information from the provided resume text and format it into a strict JSON structure that matches the following Pydantic schema. If a field is explicitly 'Not available', use null for optional fields."
f"```json\n{ResumeData.schema_json(indent=2)}\n```"
"Ensure that all relevant information from the resume and the provided text are incorporated into the report comprehensively and clearly."
                }]
        },

    ]

    response=client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},
    )
    print(f"Response: {response.choices[0].message.content}")
    json_output_str=response.choices[0].message.content
    if json_output_str:
        raw_data = json.loads(json_output_str)
    else:
        print("Error: No content received from API.")
        return None

    # Validate and parse with Pydantic
    try:
        parsed_resume_data = ResumeData(**raw_data)
    except Exception as e:
        print("Error parsing resume data:", e)
        return None

    print("Successfully parsed resume data:")
    return parsed_resume_data
# Load environment variables from .env file


if __name__ == "__main__":
    file_path = r"/Users/writwickdhivare/Desktop/Visual studio code/other/langchain_project/basic_agent/Writwick.pdf"  # Replace with your file path
    with open(file_path, "rb") as file:
        file_id=upload_file_to_openai(file)
    resume_formatting(file_id)
