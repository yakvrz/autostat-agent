# tests/test_summarizer.py
# Test script for the summarizer module

from api import main  # if needed to ensure app loads
import requests
from planner.schemas import PlanStep
from core.state import PromptState
from executor.runner import run_step
from executor.schemas import ExecutionResult
from summarizer.manager import create_analysis_report, quick_summary
from summarizer.narrative import generate_narrative, create_summary_overview
from pprint import pprint
import pandas as pd
from pathlib import Path
import json

API_URL = "http://localhost:8000"
DATASET_PATH = "example_data.csv"
PROMPT = "Explore the distribution of age and income by gender. Create visualizations and provide statistical summaries."

def upload_and_plan():
    """Upload dataset and get analysis plan from the API"""
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


def run_full_analysis():
    """Execute a complete analysis and return plan steps and results"""
    print("🔁 Uploading + planning...")
    dataset_id, raw_plan = upload_and_plan()

    print(f"\n✅ Got {len(raw_plan)} plan steps")
    df = pd.read_csv(f"data_store/{dataset_id}.csv")
    prompt_state = PromptState(question=PROMPT, profile={}, dataframe=df)

    plan_steps = []
    results = []

    for step_json in raw_plan:
        step = PlanStep(**step_json)
        plan_steps.append(step)
        
        print(f"\n🚀 Executing: [{step.tool}] {step.description}")
        result = run_step(step, prompt_state)
        results.append(result)
        
        # Print brief result info
        if result.status == "success":
            print(f"   ✅ Success - Artifact: {result.artifact_path or 'None'}")
        else:
            print(f"   ❌ Error: {result.error}")

    return plan_steps, results


def test_narrative_generation():
    """Test the narrative generation components"""
    print("\n" + "="*60)
    print("🧪 TESTING NARRATIVE GENERATION")
    print("="*60)
    
    # Create mock data for testing
    mock_steps = [
        PlanStep(
            step_id="step_1",
            tool="explore_data",
            description="Basic exploration of the dataset structure",
            args={"action": "overview"}
        ),
        PlanStep(
            step_id="step_2",
            tool="create_histogram",
            description="Create histogram of age distribution",
            args={"column": "age", "bins": 20}
        )
    ]
    
    mock_results = [
        ExecutionResult(
            step_id="step_1",
            status="success",
            output_preview={"row_count": 1000, "column_count": 5, "null_values": 12},
            artifact_path=None
        ),
        ExecutionResult(
            step_id="step_2", 
            status="success",
            output_preview=None,
            artifact_path="artifacts/histogram_abc123.png"
        )
    ]
    
    # Test narrative generation
    print("\n📖 Testing narrative generation...")
    narrative_sections = generate_narrative(mock_steps, mock_results)
    
    print(f"Generated {len(narrative_sections)} sections:")
    for title, content in narrative_sections.items():
        print(f"\n--- {title} ---")
        print(content[:200] + "..." if len(content) > 200 else content)
    
    # Test overview generation
    print("\n📊 Testing overview generation...")
    overview = create_summary_overview(mock_steps, mock_results)
    print(overview[:300] + "..." if len(overview) > 300 else overview)
    
    # Test quick summary
    print("\n⚡ Testing quick summary...")
    summary = quick_summary(mock_steps, mock_results)
    print(f"Quick summary: {summary}")


def test_full_summarizer():
    """Test the complete summarizer workflow with real data"""
    print("\n" + "="*60)
    print("🧪 TESTING FULL SUMMARIZER WORKFLOW")
    print("="*60)
    
    try:
        # Run analysis
        plan_steps, results = run_full_analysis()
        
        print(f"\n📝 Analysis completed with {len(results)} results")
        
        # Test quick summary
        summary = quick_summary(plan_steps, results)
        print(f"\n⚡ Quick summary: {summary}")
        
        # Create full report
        print("\n📄 Creating comprehensive report...")
        report_path = create_analysis_report(
            plan_steps, 
            results,
            output_dir="test_reports",
            report_name="test_analysis.md"
        )
        
        print(f"✅ Report created: {report_path}")
        
        # Verify report was created and has content
        if report_path.exists():
            content = report_path.read_text()
            print(f"📊 Report size: {len(content)} characters")
            print(f"📈 First 300 characters:\n{content[:300]}...")
            
            # Count sections
            section_count = content.count("##")
            print(f"📋 Report contains {section_count} sections")
        else:
            print("❌ Report file was not created!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        raise


def test_error_handling():
    """Test error handling in summarizer"""
    print("\n" + "="*60)
    print("🧪 TESTING ERROR HANDLING")
    print("="*60)
    
    # Test with failed step
    steps = [
        PlanStep(
            step_id="error_step",
            tool="broken_tool", 
            description="This will fail", 
            args={}
        )
    ]
    
    results = [
        ExecutionResult(
            step_id="error_step",
            status="error",
            error="Tool 'broken_tool' not found in registry"
        )
    ]
    
    print("📖 Testing narrative with errors...")
    narrative = generate_narrative(steps, results)
    print(narrative["Broken Tool"][:200] + "...")
    
    print("\n📊 Testing overview with errors...")
    overview = create_summary_overview(steps, results)
    print(overview[:300] + "...")
    
    print("\n⚡ Testing quick summary with errors...")
    summary = quick_summary(steps, results)
    print(f"Summary: {summary}")


if __name__ == "__main__":
    print("🧪 AutoStat-Agent Summarizer Tests")
    print("=" * 60)
    
    # Run different test suites
    test_narrative_generation()
    test_error_handling()
    
    # Try to run full test with real API
    try:
        test_full_summarizer()
    except Exception as e:
        print(f"\n⚠️  Full API test failed: {e}")
        print("This is expected if the API server is not running")
    
    print("\n🎉 All tests completed!") 