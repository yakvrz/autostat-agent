# executor/tools/stats.py
# Statistical test implementations (e.g., t-test, ANOVA).

import uuid
import os
import pandas as pd
from scipy import stats
import json
from typing import Dict, Optional, Any

# Constants
ARTIFACTS_DIR = "artifacts"
EXPECTED_T_TEST_GROUPS = 2


def run_t_test(
    df: pd.DataFrame,
    group_column: str,
    value_column: str,
    equal_var: bool = False,
) -> Dict[str, Optional[Any]]:
    """
    Perform an independent-samples t-test comparing values between two groups.
    
    Uses Welch's t-test by default (equal_var=False) which doesn't assume equal variances.
    
    Args:
        df: The input DataFrame
        group_column: Column name containing group labels (must have exactly 2 unique values)
        value_column: Column name containing numeric values to compare
        equal_var: If True, assumes equal variances (Student's t-test). 
                  If False, uses Welch's t-test (default)
    
    Returns:
        Dictionary with 'preview' (test results dict) and 'artifact' (JSON file path)
        
    Raises:
        ValueError: If group_column doesn't contain exactly 2 groups
    """
    groups = df[group_column].dropna().unique()
    if len(groups) != EXPECTED_T_TEST_GROUPS:
        raise ValueError(
            f"t_test expects exactly {EXPECTED_T_TEST_GROUPS} groups in '{group_column}', "
            f"found {len(groups)}."
        )

    g1, g2 = groups
    v1 = df.loc[df[group_column] == g1, value_column].dropna()
    v2 = df.loc[df[group_column] == g2, value_column].dropna()

    t_stat, p_val = stats.ttest_ind(v1, v2, equal_var=equal_var)

    preview = {
        "group_1": str(g1),
        "group_2": str(g2),
        "n_1": int(v1.size),
        "n_2": int(v2.size),
        "mean_1": float(v1.mean()),
        "mean_2": float(v2.mean()),
        "t_stat": float(t_stat),
        "p_value": float(p_val),
    }

    # Save full result to JSON artifact
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    artifact_path = f"{ARTIFACTS_DIR}/ttest_{uuid.uuid4().hex[:8]}.json"
    with open(artifact_path, "w") as f:
        json.dump(preview, f, indent=2)

    return {"preview": preview, "artifact": artifact_path}