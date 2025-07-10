# summarizer/narrative.py
# Constructs final summary of the executed analysis plan.

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from planner.schemas import PlanStep
from executor.schemas import ExecutionResult


def generate_narrative(plan_steps: List[PlanStep], results: List[ExecutionResult]) -> Dict[str, str]:
    """
    Generate narrative text blocks for each step in the analysis plan.
    
    Args:
        plan_steps: List of planned analysis steps
        results: List of execution results corresponding to each step
        
    Returns:
        Dictionary with section titles and corresponding markdown text
    """
    section_texts = {}

    for step, result in zip(plan_steps, results):
        # Create section title from tool name
        title = step.tool.replace('_', ' ').title()
        summary = f"## {title}\n\n"
        summary += f"**Description:** {step.description}\n\n"

        if result.status == "error":
            summary += f"❌ **Error:** {result.error}\n\n"
        else:
            summary += "✅ **Status:** Completed successfully\n\n"
            
            # Add preview data if available
            if result.output_preview:
                summary += "**Results:**\n\n"
                if isinstance(result.output_preview, dict):
                    # Format as key-value pairs
                    for key, value in result.output_preview.items():
                        summary += f"- **{key}:** {value}\n"
                elif isinstance(result.output_preview, list) and result.output_preview:
                    # Format as table if it's a list of dicts
                    if isinstance(result.output_preview[0], dict):
                        summary += _format_table(result.output_preview)
                    else:
                        summary += f"- {', '.join(map(str, result.output_preview))}\n"
                summary += "\n"
            
            # Add artifact reference if available
            if result.artifact_path:
                artifact_name = Path(result.artifact_path).name
                if result.artifact_path.endswith(('.png', '.jpg', '.jpeg')):
                    summary += f"**Visualization:**\n\n![{title}]({result.artifact_path})\n\n"
                elif result.artifact_path.endswith('.json'):
                    # Try to read and display JSON artifacts
                    try:
                        if os.path.exists(result.artifact_path):
                            with open(result.artifact_path, 'r') as f:
                                data = json.load(f)
                            summary += f"**Statistical Results:**\n\n```json\n{json.dumps(data, indent=2)}\n```\n\n"
                    except Exception as e:
                        summary += f"**Artifact:** {artifact_name} (could not display: {e})\n\n"
                else:
                    summary += f"**Generated file:** `{artifact_name}`\n\n"

        section_texts[title] = summary

    return section_texts


def _format_table(data: List[Dict[str, Any]]) -> str:
    """
    Format list of dictionaries as a markdown table.
    
    Args:
        data: List of dictionaries with consistent keys
        
    Returns:
        Markdown table string
    """
    if not data:
        return ""
    
    # Get headers from first item
    headers = list(data[0].keys())
    
    # Create table header
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # Add rows
    for row in data[:10]:  # Limit to first 10 rows
        values = [str(row.get(h, "")) for h in headers]
        table += "| " + " | ".join(values) + " |\n"
    
    if len(data) > 10:
        table += f"\n*Showing first 10 of {len(data)} rows*\n"
    
    return table + "\n"


def create_summary_overview(plan_steps: List[PlanStep], results: List[ExecutionResult]) -> str:
    """
    Create a high-level overview section for the report.
    
    Args:
        plan_steps: List of planned analysis steps
        results: List of execution results
        
    Returns:
        Markdown text for overview section
    """
    total_steps = len(plan_steps)
    successful_steps = sum(1 for r in results if r.status == "success")
    failed_steps = total_steps - successful_steps
    
    overview = "# Analysis Summary\n\n"
    overview += f"**Total Steps:** {total_steps}\n"
    overview += f"**Successful:** {successful_steps} ✅\n"
    overview += f"**Failed:** {failed_steps} ❌\n\n"
    
    if failed_steps > 0:
        overview += "## ⚠️ Issues Encountered\n\n"
        for step, result in zip(plan_steps, results):
            if result.status == "error":
                overview += f"- **{step.tool}**: {result.error}\n"
        overview += "\n"
    
    # List the analysis steps performed
    overview += "## Analysis Steps Performed\n\n"
    for i, step in enumerate(plan_steps, 1):
        status_icon = "✅" if results[i-1].status == "success" else "❌"
        overview += f"{i}. {status_icon} **{step.tool.replace('_', ' ').title()}**: {step.description}\n"
    
    overview += "\n---\n\n"
    return overview