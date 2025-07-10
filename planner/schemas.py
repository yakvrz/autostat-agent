# planner/schemas.py
# Pydantic models for Plan, PlanStep, and validation helpers.

from pydantic import BaseModel
from typing import Dict, List, Any

# Represents a single step in a plan, such as a tool invocation with arguments.
class PlanStep(BaseModel):
    step_id: str  # Unique identifier for the step.
    description: str  # Human-readable description of the step.
    tool: str  # Name of the tool or function to invoke.
    args: Dict[str, Any]  # Arguments to pass to the tool.

class Plan(BaseModel):
    steps: List[PlanStep]
