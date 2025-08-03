import os
import json
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from src.models import TaskData

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def task_formatting(task_description: str):
    """
    Analyzes a task description and returns a structured TaskData object.
    """
    prompt = f"""
You are an expert project manager. Your task is to analyze the following task description and extract structured information.

**Task Description:**
{task_description}

**Instructions:**
- Analyze the task description thoroughly.
- Extract the task name, a detailed description, an estimated time for completion, and a list of required skills.
- Format the output as a JSON object that matches the following Pydantic schema.
```json
{TaskData.schema_json(indent=2)}
```
Ensure that all relevant information from the task description is incorporated into the report comprehensively and clearly.
"""

    messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"}
    )

    json_output_str = response.choices[0].message.content
    if not json_output_str:
        print("Error: No content received from API.")
        return None
    raw_data = json.loads(json_output_str)
    print(f"Raw data received: {raw_data}")
    try:
        parsed_task_data = TaskData(**raw_data)
        return parsed_task_data
    except Exception as e:
        print(f"Error parsing task data: {e}")
        return None

if __name__ == '__main__':
    description = "Create a new landing page for our website. It should be responsive and include a contact form. This should take about 3 days and requires knowledge of HTML, CSS, and JavaScript."
    task_data = task_formatting(description)
    if task_data:
        print("Successfully parsed task data:")
        print(task_data.json(indent=2))
