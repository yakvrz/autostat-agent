# tests/test_planner.py

import requests

API_URL = "http://localhost:8000"
DATASET_PATH = "example_data.csv"
PROMPT = "What is the distribution of age and income by gender?"

def upload_dataset():
    with open(DATASET_PATH, "rb") as f:
        files = {"file": (DATASET_PATH, f, "text/csv")}
        resp = requests.post(f"{API_URL}/datasets/upload", files=files)
        resp.raise_for_status()
        data = resp.json()
        print("✅ Uploaded dataset. ID:", data["dataset_id"])
        return data["dataset_id"], data["profile"]

def analyze_dataset(dataset_id):
    data = {
        "dataset_id": dataset_id,
        "prompt": PROMPT
    }
    resp = requests.post(f"{API_URL}/analyze", data=data)
    resp.raise_for_status()
    result = resp.json()
    print("✅ Received analysis plan with", len(result["plan"]), "steps.")
    return result

if __name__ == "__main__":
    print("🔁 Uploading dataset...")
    dataset_id, profile = upload_dataset()

    print("\n📊 Running analysis plan...")
    result = analyze_dataset(dataset_id)

    print("\n--- Analysis Plan ---")
    for step in result["plan"]:
        print(f"[{step['tool']}] {step['description']} → args: {step['args']}")
