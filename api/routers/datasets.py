# api/routers/datasets.py
# Manages dataset upload, metadata, and retrieval endpoints.

from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import uuid
import os

from datasets.profile import profile_dataset
from datasets.storage import save_dataset

router = APIRouter()


@router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(..., description="CSV file containing the dataset to analyze")
) -> JSONResponse:
    """
    Upload and process a CSV dataset for analysis.
    
    This endpoint accepts a CSV file, loads it into a DataFrame, generates
    a data profile with summary statistics, and stores both the dataset
    and its profile for later use.
    
    Args:
        file: CSV file upload containing the dataset
        
    Returns:
        JSON response with the dataset ID and profile information
        
    Raises:
        HTTPException: If the CSV file cannot be parsed or processed
    """
    # Step 1: Attempt to load the uploaded file as a CSV into a pandas DataFrame
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        # If loading fails, return a 400 error with details
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")

    # Step 2: Generate a profile (summary/statistics) of the dataset
    profile = profile_dataset(df)

    # Step 3: Generate a unique ID for the dataset and save both the data and its profile
    dataset_id = str(uuid.uuid4())
    save_dataset(dataset_id, df, profile)

    # Step 4: Return the dataset ID and its profile in the response
    return JSONResponse(content={
        "dataset_id": dataset_id,
        "profile": profile
    })