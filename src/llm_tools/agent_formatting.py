import os
import json
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from src.models import AgentData

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def agent_formatting(agent_description: str):
    """
    Analyzes an agent description and returns a structured AgentData object.
    """
    prompt = f"""
You are an expert AI architect. Your task is to analyze the following agent description and extract structured information.

**Agent Description:**
{agent_description}

**Instructions:**
- Analyze the agent description thoroughly.
- Extract the tags, skills, capabilities, and core functionalities.
- Format the output as a JSON object that matches the following Pydantic schema.
```json
{AgentData.schema_json(indent=2)}
```
Ensure that all relevant information from the agent description is incorporated into the report comprehensively and clearly.
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
        parsed_agent_data = AgentData(**raw_data)
        return parsed_agent_data
    except Exception as e:
        print(f"Error parsing agent data: {e}")
        return None

if __name__ == '__main__':
    description = "This agent is designed for customer support. It can understand and respond to user queries in natural language, integrate with our CRM to fetch customer data, and escalate complex issues to a human agent. Its main job is to answer frequently asked questions and guide users through our product features."
    agent_data = agent_formatting(description)
    if agent_data:
        print("Successfully parsed agent data:")
        print(agent_data.json(indent=2))
