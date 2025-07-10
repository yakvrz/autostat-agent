# executor/tools/eda.py
# Exploratory Data Analysis (EDA) tools for the executor component.

import pandas as pd
from typing import Dict, List, Optional, Any, Union


def _flatten_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert MultiIndex columns to flat column names by joining with underscores.
    
    Example: ('age', 'mean') becomes 'age_mean'
    Leaves single-level columns unchanged.
    
    Args:
        df: DataFrame with potentially MultiIndex columns
        
    Returns:
        DataFrame with flattened column names
    """
    if not isinstance(df.columns, pd.MultiIndex):
        return df

    df = df.copy()
    df.columns = [
        "_".join(str(part) for part in col if part != "")
        if isinstance(col, tuple) else str(col)
        for col in df.columns
    ]
    return df


def run_summary_stats(
    df: pd.DataFrame,
    columns: List[str],
    by: Optional[str] = None,
) -> Dict[str, Optional[Any]]:
    """
    Generate descriptive statistics for specified columns, optionally grouped.
    
    Args:
        df: The input DataFrame
        columns: List of numeric column names to analyze
        by: Optional grouping column name
        
    Returns:
        Dictionary with 'preview' (list of records) and 'artifact' (None)
    """
    # Ungrouped analysis: simple describe() with stats as rows
    if by is None:
        preview_df = (
            df[columns]
            .describe()
            .T.reset_index()
            .rename(columns={"index": "column"})
        )
        preview = preview_df.to_dict(orient="records")
        return {"preview": preview, "artifact": None}

    # Grouped analysis: describe() after groupby
    described = df.groupby(by)[columns].describe().reset_index()
    described = _flatten_cols(described)

    # Ensure grouping column stays first for readability
    col_order = [by] + [c for c in described.columns if c != by]
    described = described[col_order]

    preview = described.to_dict(orient="records")
    return {"preview": preview, "artifact": None}


def run_eda_overview(df: pd.DataFrame) -> Dict[str, Optional[Any]]:
    """
    Generate a high-level overview of the dataset structure and missing values.
    
    Args:
        df: The input DataFrame to analyze
        
    Returns:
        Dictionary with 'preview' (dataset profile dict) and 'artifact' (None)
    """
    profile = {
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "columns": list(df.columns),
        "missing": df.isnull().sum().to_dict()
    }
    return {"preview": profile, "artifact": None}