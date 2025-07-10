# executor/registry.py
# Maps tool names to callable tool implementations.

from executor.tools.eda import run_eda_overview
from executor.tools.eda import run_summary_stats
from executor.tools.plotting import run_histogram
from executor.tools.plotting import run_boxplot
from executor.tools.stats import run_t_test

TOOL_REGISTRY = {
    "eda_overview": run_eda_overview,
    "summary_stats": run_summary_stats,
    "histogram": run_histogram,
    "boxplot": run_boxplot,
    "t_test": run_t_test,
    # add more as needed
}