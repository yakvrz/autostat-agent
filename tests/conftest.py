from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]  # project root
sys.path.insert(0, str(ROOT))  # make "api", "app", etc. importable
