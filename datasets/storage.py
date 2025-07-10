# datasets/storage.py
# Manages local file paths, identifiers, and metadata indexing.

import os
import pandas as pd
import json
from typing import Dict, Any, Tuple

# Constants
BASE_DIR = "data_store"
CSV_EXTENSION = ".csv"
METADATA_EXTENSION = ".meta.json"


def _ensure_dir() -> None:
    """
    Ensure that the base directory for storing datasets exists.
    Creates the directory if it doesn't already exist.
    """
    os.makedirs(BASE_DIR, exist_ok=True)


def save_dataset(dataset_id: str, df: pd.DataFrame, profile: Dict[str, Any]) -> None:
    """
    Save a DataFrame and its associated profile metadata to disk.

    Files are saved with the dataset_id as the base filename:
    - Dataset: {dataset_id}.csv
    - Metadata: {dataset_id}.meta.json

    Args:
        dataset_id: Unique identifier for the dataset
        df: The dataset to save as CSV
        profile: Metadata/profile information to save as JSON

    Note:
        The DataFrame is saved without the index to keep CSV files clean.
    """
    _ensure_dir()
    
    df_path = os.path.join(BASE_DIR, f"{dataset_id}{CSV_EXTENSION}")
    meta_path = os.path.join(BASE_DIR, f"{dataset_id}{METADATA_EXTENSION}")
    
    # Save the DataFrame as a CSV file without index
    df.to_csv(df_path, index=False)
    
    # Save the profile metadata as a JSON file
    with open(meta_path, "w") as f:
        json.dump(profile, f)


def load_dataset(dataset_id: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load a DataFrame and its associated profile metadata from disk.

    Args:
        dataset_id: Unique identifier for the dataset

    Returns:
        Tuple containing the loaded dataset and its profile metadata

    Raises:
        FileNotFoundError: If the dataset CSV file does not exist
        json.JSONDecodeError: If the metadata file is corrupted
    """
    df_path = os.path.join(BASE_DIR, f"{dataset_id}{CSV_EXTENSION}")
    meta_path = os.path.join(BASE_DIR, f"{dataset_id}{METADATA_EXTENSION}")
    
    if not os.path.exists(df_path):
        raise FileNotFoundError(f"Dataset {dataset_id} not found at {df_path}")
    
    # Load the DataFrame from the CSV file
    df = pd.read_csv(df_path)
    
    # Load the profile metadata from the JSON file
    with open(meta_path) as f:
        profile = json.load(f)
    
    return df, profile