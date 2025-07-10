# api/routers/analyze.py
# Handles /analyze endpoint for dataset analysis requests.

from typing import Dict, Any
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse

from core.state import PromptState
from datasets.storage import load_dataset
from planner.llm_planner import plan

router = APIRouter()


@router.post("/analyze")
async def analyze(
    dataset_id: str = Form(..., description="Unique identifier for the uploaded dataset"),
    prompt: str = Form(..., description="Research question or analysis request")
) -> JSONResponse:
    """
    Generate an analysis plan for a given dataset and research question.
    
    This endpoint loads the specified dataset, builds a prompt state with the 
    user's question and dataset profile, then generates a structured plan 
    using the LLM planner.
    
    Args:
        dataset_id: Unique identifier for a previously uploaded dataset
        prompt: The user's research question or analysis request
        
    Returns:
        JSON response containing the dataset profile and generated analysis plan
        
    Raises:
        HTTPException: If the dataset cannot be loaded or planning fails
    """
    # Step 1: Load the dataset and its profile using the provided dataset_id
    df, profile = load_dataset(dataset_id)

    # Step 2: Build a PromptState object to encapsulate the user's question,
    # the loaded dataframe, and its profile for downstream processing
    prompt_state = PromptState(
        question=prompt,
        dataframe=df,
        profile=profile
    )

    # Step 3: Generate a plan using the planner module
    plan_steps = plan(prompt_state)

    # Step 4: Return the dataset_id, profile, and the generated plan as a JSON response
    return JSONResponse(content={
        "dataset_id": dataset_id,
        "profile": profile,
        "plan": [step.model_dump() for step in plan_steps]
    })