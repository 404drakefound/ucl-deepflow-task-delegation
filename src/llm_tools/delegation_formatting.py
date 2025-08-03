import os
import json
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field
from typing import List, Dict
from dotenv import load_dotenv
from src.models import DelegationResult

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def delegate_task(task_details: dict, member_details: List[dict], agent_details: List[dict]):
    """
    Analyzes task, member, and agent details to recommend the best combination.
    """
    print("delegate_error")

    prompt = f"""
You are an expert project manager and AI strategist. Your task is to analyze the following task, and the recommended members and agents, to determine the absolute best combination to complete the task efficiently and effectively.

**Task Details:**
{str(task_details)}

**Top 3 Recommended Members:**
{str(member_details)}

**Top 3 Recommended Agents:**
{str(agent_details)}

**Instructions:**
- Analyze the task requirements, member skills, and agent capabilities.
- Determine the best combination of members and/or agents to perform the task.
- You can choose any number of members and agents from the provided lists.
- Provide a detailed reasoning for your choice.
- Format the output as a JSON object that matches the following Pydantic schema.
```json
{DelegationResult.schema_json(indent=2)}
```
"""
    print("llm error")
    messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": prompt,
        }
    ]
    print("message erro")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"}
    )
    print("formatting error")
    json_output_str = response.choices[0].message.content
    if not json_output_str:
        print("Error: No content received from API.")
        return None
    raw_data = json.loads(json_output_str)
    print(f"Raw data received: {raw_data}")
    try:
        parsed_delegation_data = DelegationResult(**raw_data)
        return parsed_delegation_data
    except Exception as e:
        print(f"Error parsing delegation data: {e}")
        return None
