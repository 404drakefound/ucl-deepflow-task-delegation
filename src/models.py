from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ResumeData(BaseModel):
    """
    Pydantic class to model the structured output of an LLM for resume analysis.
    """
    personal_summary: str = Field(..., description="A concise summary of the candidate's professional aspirations and focus.")
    technical_skills: List[str] = Field(..., description="A list of technical proficiencies.")
    certifications: List[str] = Field(..., description="A list of professional certifications obtained.")
    soft_skills: List[str] = Field(..., description="A list of interpersonal and non-technical abilities.")
    vocal_attributes: Optional[str] = Field(None, description="Information regarding vocal attributes, if available.")
    task_delegation_recommendations: List[str] = Field(..., description="Recommended tasks or responsibilities for the candidate.")
    specialization_task_categories: List[str] = Field(..., description="Categories of specialized tasks the candidate is suited for.")
    additional_observations: List[str] = Field(..., description="Any other notable observations about the candidate.")

class TaskData(BaseModel):
    """
    Pydantic class to model the structured output of an LLM for task analysis.
    """
    required_skills: List[str] = Field(..., description="A list (list of string) of skills required to complete the task.")
    sector: Optional[str] = Field(None, description="(list of string) The relevant industry, department, or domain for this task (e.g., 'Finance', 'Marketing', 'Backend Development', 'HR').")
    tags: List[str] = Field(default_factory=list, description="(list of string) Relevant keywords or labels for categorization and matching, including project names, technologies, or departments.")
    manpower_needed: int  = Field(..., description="(only integer) The estimated number of individuals")
    roles_required: List[str] = Field(default_factory=list, description=" or type of team roles required (e.g., 'developers', 'a small QA team', 'project manager').")
    estimated_time: int = Field(..., description="(only integer)An estimation of the number of hours required to complete the task (e.g., 2, 21).")

class AgentData(BaseModel):
    """
    Pydantic class to model the structured output of an LLM for agent analysis,
    focusing on core attributes derivable from a summary.
    """
    tags: List[str] = Field(default_factory=list, description="Relevant keywords or labels for categorizing the agent (e.g., 'customer service', 'automation', 'reporting').")
    skills: List[str] = Field(default_factory=list, description="A list of specific abilities or proficiencies the agent possesses (e.g., 'Natural Language Processing', 'API Integration', 'Data Validation').")
    capabilities: List[str] = Field(default_factory=list, description="A list of higher-level functionalities or complex actions the agent can perform (e.g., 'Understand customer intent', 'Generate marketing copy', 'Automate workflow').")
    core_functionalities: List[str] = Field(default_factory=list, description="A list of the fundamental tasks or primary purposes the agent is designed to execute (e.g., 'Answer FAQs', 'Process payments', 'Extract data from documents').")

class DelegationResult(BaseModel):
    """
    Pydantic class to model the structured output of an LLM for task delegation.
    """
    best_combination: Dict[str, str] = Field(..., description="A dictionary where keys are member or agent IDs with prefix member/agent, so the key will be of this format 'type_id', where type can be either member or agent, id being the primary key and not the deepflow_id, and values are the reasons for their selection.")
    reasoning: str = Field(..., description="A detailed explanation of why this combination is the best for the task.")
