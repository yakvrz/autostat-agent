# executor/schemas.py
# Pydantic models for execution results and related data structures.

from typing import Optional, Dict, Any, List, Union, Literal
from pydantic import BaseModel, Field

# Type alias for execution status
ExecutionStatus = Literal["success", "error"]


class ExecutionResult(BaseModel):
    """
    Result of executing a single plan step.
    
    Contains the execution status, any output preview data, 
    file artifacts generated, and error information if applicable.
    """
    step_id: str = Field(..., description="Unique identifier for the executed step")
    status: ExecutionStatus = Field(..., description="Execution status: 'success' or 'error'")
    output_preview: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None, description="Preview of the execution output (e.g., summary statistics, data sample)"
    )
    artifact_path: Optional[str] = Field(
        None, description="Path to generated artifact file (e.g., plot, report)"
    )
    error: Optional[str] = Field(
        None, description="Error message if status is 'error'"
    )