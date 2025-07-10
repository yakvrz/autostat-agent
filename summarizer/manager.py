# summarizer/manager.py
# Main summarizer orchestration functions for creating analysis reports.

from pathlib import Path
from typing import List, Optional
from datetime import datetime

from planner.schemas import PlanStep
from executor.schemas import ExecutionResult
from summarizer.narrative import generate_narrative, create_summary_overview
from summarizer.render import render_markdown_report


def create_analysis_report(
    plan_steps: List[PlanStep], 
    results: List[ExecutionResult],
    output_dir: str = "reports",
    report_name: Optional[str] = None
) -> Path:
    """
    Create a comprehensive analysis report from plan steps and execution results.
    
    Args:
        plan_steps: List of analysis steps that were planned
        results: List of execution results for each step
        output_dir: Directory to save the report
        report_name: Custom name for the report file (auto-generated if None)
        
    Returns:
        Path to the generated markdown report
        
    Raises:
        ValueError: If plan_steps and results have different lengths
    """
    if len(plan_steps) != len(results):
        raise ValueError(f"Mismatch: {len(plan_steps)} plan steps but {len(results)} results")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate report filename if not provided
    if report_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"analysis_report_{timestamp}.md"
    
    report_path = output_path / report_name
    
    # Generate narrative sections
    overview = create_summary_overview(plan_steps, results)
    sections = generate_narrative(plan_steps, results)
    
    # Combine overview with detailed sections
    all_sections = {"overview": overview}
    all_sections.update(sections)
    
    # Render to markdown file
    final_path = render_markdown_report(all_sections, report_path)
    
    return final_path


def quick_summary(plan_steps: List[PlanStep], results: List[ExecutionResult]) -> str:
    """
    Generate a quick text summary of the analysis results.
    
    Args:
        plan_steps: List of analysis steps that were planned
        results: List of execution results for each step
        
    Returns:
        Brief text summary of the analysis
    """
    if len(plan_steps) != len(results):
        return f"Error: Mismatch between {len(plan_steps)} planned steps and {len(results)} results"
    
    total_steps = len(plan_steps)
    successful_steps = sum(1 for r in results if r.status == "success")
    failed_steps = total_steps - successful_steps
    
    summary = f"Analysis completed: {successful_steps}/{total_steps} steps successful"
    
    if failed_steps > 0:
        failed_tools = [step.tool for step, result in zip(plan_steps, results) if result.status == "error"]
        summary += f" ({failed_steps} failed: {', '.join(failed_tools)})"
    
    return summary 