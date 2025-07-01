from pathlib import Path
import duckdb
import pandas as pd
from ydata_profiling import ProfileReport

_DB = duckdb.connect("autostat.duckdb")


def create_profile(csv_path: Path) -> Path:
    """Load the CSV, build a minimal HTML profile, and register it in DuckDB."""
    df = pd.read_csv(csv_path)

    report = ProfileReport(df, minimal=True)
    out_path = csv_path.with_suffix(".profile.html")
    report.to_file(out_path)

    _DB.execute(
        "INSERT INTO dataset_meta VALUES (?, ?, ?)",
        [csv_path.parent.name, csv_path.name, out_path.name],
    )
    print("✅ INSERTED row for", csv_path.name)
    return out_path
