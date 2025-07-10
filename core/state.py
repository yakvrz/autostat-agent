# core/state.py
# Maintains shared data models such as PromptState and RunResult

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import pandas as pd

# Represents the state of a prompt, including the question, user profile, and an optional DataFrame.
class PromptState(BaseModel):
    question: str  # The user's question or prompt.
    profile: Dict[str, Any]  # User profile or context information.
    # DataFrame is used internally for data processing, not included in serialized API responses.
    dataframe: Optional[pd.DataFrame] = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True  # Allow non-pydantic types like pd.DataFrame.