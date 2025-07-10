# executor/runner.py
# Orchestrates the execution of PlanStep, including artefact handling.

from typing import Optional
from core.state import PromptState
from planner.schemas import PlanStep
from executor.schemas import ExecutionResult
from executor.registry import TOOL_REGISTRY
from executor.utils import coerce_args, validate_args


def run_step(step: PlanStep, ctx: PromptState) -> ExecutionResult:
    """
    Execute a single plan step using the appropriate tool.
    
    Args:
        step: The plan step containing tool name, arguments, and metadata
        ctx: Context containing the dataset and other execution state
        
    Returns:
        ExecutionResult with success/error status and any artifacts produced
    """
    tool_fn = TOOL_REGISTRY.get(step.tool)
    if not tool_fn:
        return ExecutionResult(
            step_id=step.step_id,
            status="error",
            error=f"Tool '{step.tool}' not found"
        )

    # Central argument coercion and validation
    safe_args = coerce_args(step.tool, step.args)

    # Re-validate after coercion
    is_valid, validation_error = validate_args(step.tool, safe_args)
    if not is_valid:
        return ExecutionResult(
            step_id=step.step_id,
            status="error",
            error=f"Arg validation failed: {validation_error}"
        )

    # Execute the tool
    try:
        output = tool_fn(ctx.dataframe, **safe_args)
        return ExecutionResult(
            step_id=step.step_id,
            status="success",
            output_preview=output.get("preview"),
            artifact_path=output.get("artifact")
        )
    except Exception as exc:
        return ExecutionResult(
            step_id=step.step_id,
            status="error",
            error=str(exc)
        )
