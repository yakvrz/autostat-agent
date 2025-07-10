# tests/test_executor.py

from api import main  # if needed to ensure app loads
import requests
from planner.schemas import PlanStep
from core.state import PromptState
from executor.runner import run_step
from pprint import pprint
import pandas as pd

API_URL = "http://localhost:8000"
DATASET_PATH = "example_data.csv"
PROMPT = "Explore the distribution of age and income by gender."

def upload_and_plan():
    with open(DATASET_PATH, "rb") as f:
        files = {"file": (DATASET_PATH, f, "text/csv")}
        upload_resp = requests.post(f"{API_URL}/datasets/upload", files=files)
        upload_resp.raise_for_status()
        dataset_id = upload_resp.json()["dataset_id"]

    data = {"dataset_id": dataset_id, "prompt": PROMPT}
    plan_resp = requests.post(f"{API_URL}/analyze", data=data)
    plan_resp.raise_for_status()

    plan = plan_resp.json()["plan"]
    return dataset_id, plan

if __name__ == "__main__":
    print("🔁 Uploading + planning...")
    dataset_id, raw_plan = upload_and_plan()

    print(f"\n✅ Got {len(raw_plan)} plan steps")
    df = pd.read_csv(f"data_store/{dataset_id}.csv")
    prompt_state = PromptState(question=PROMPT, profile={}, dataframe=df)

    for step_json in raw_plan:
        step = PlanStep(**step_json)
        print(f"\n🚀 Executing: [{step.tool}] {step.description}")
        result = run_step(step, prompt_state)
        pprint(result.model_dump())
