# datasets/profile.py
# Dataset profiling (column names, types, nulls, etc.).

import pandas as pd

def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate a simple profile of a pandas DataFrame, including row/column counts,
    column data types, missing values, and basic statistics for numeric and categorical columns.
    """
    profile = {
        "num_rows": len(df),  # Total number of rows in the DataFrame
        "num_columns": len(df.columns),  # Total number of columns
        "columns": {}  # Dictionary to hold per-column profiling info
    }

    for col in df.columns:
        series = df[col]
        col_profile = {
            "dtype": str(series.dtype),  # Data type of the column
            "num_missing": int(series.isna().sum()),  # Number of missing (NaN) values
        }

        # If the column is numeric, compute basic statistics
        if pd.api.types.is_numeric_dtype(series):
            col_profile["mean"] = float(series.mean())
            col_profile["std"] = float(series.std())
            col_profile["min"] = float(series.min())
            col_profile["max"] = float(series.max())
        # If the column is categorical or object, show top 5 most frequent values
        elif pd.api.types.is_categorical_dtype(series) or pd.api.types.is_object_dtype(series):
            vc = series.value_counts(dropna=True).head(5)
            col_profile["top_values"] = vc.to_dict()

        profile["columns"][col] = col_profile  # Add column profile to the result

    return profile  # Return the complete profile dictionary
