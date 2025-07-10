# executor/tools/plotting.py
# Plotting tools for the executor component, providing visualizations like boxplots and histograms.

import matplotlib.pyplot as plt
import pandas as pd
import uuid
import os
from typing import Dict, List, Optional, Any

# Constants
ARTIFACTS_DIR = "artifacts"
DEFAULT_HISTOGRAM_BINS = 20


def run_histogram(df: pd.DataFrame, columns: List[str]) -> Dict[str, Optional[Any]]:
    """
    Generate histograms for the specified numeric columns.
    
    Args:
        df: The input DataFrame
        columns: List of column names to create histograms for
        
    Returns:
        Dictionary with 'preview' (None) and 'artifact' (file path)
    """
    path = f"{ARTIFACTS_DIR}/hist_{uuid.uuid4().hex[:8]}.png"
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    df[columns].hist(bins=DEFAULT_HISTOGRAM_BINS)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return {"preview": None, "artifact": path}


def run_boxplot(df: pd.DataFrame, x: str, y: str) -> Dict[str, Optional[Any]]:
    """
    Create a box-and-whisker plot of numeric variable grouped by categorical variable.
    
    Args:
        df: The input DataFrame
        x: Grouping/category column name (plotted on x-axis)
        y: Numeric column name whose distribution is plotted (y-axis)
        
    Returns:
        Dictionary with 'preview' (None) and 'artifact' (file path)
    """
    path = f"{ARTIFACTS_DIR}/box_{uuid.uuid4().hex[:8]}.png"
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    df.boxplot(column=[y], by=x)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return {"preview": None, "artifact": path}
