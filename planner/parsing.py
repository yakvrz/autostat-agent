# planner/parsing.py
# JSON parsing and plan creation utilities for LLM responses.

import json
import uuid
import re
from typing import List, Optional
from planner.schemas import PlanStep


def parse_plan(response_text: str, log_dir: Optional[str] = None) -> List[PlanStep]:
    """
    Parse the raw LLM response into PlanStep list.
    
    Attempts strict JSON parsing first, then falls back to extracting
    JSON array from markdown or prose responses.
    
    Args:
        response_text: Raw text response from the LLM
        log_dir: Optional directory to write parsing error logs
        
    Returns:
        List of validated PlanStep objects
        
    Raises:
        ValueError: If no valid JSON array can be extracted
    """
    from planner.logging import log_plan_stage
    
    try:
        # First try strict JSON parse
        raw_steps = json.loads(response_text)
        return _load_plan_steps(raw_steps)

    except json.JSONDecodeError as e:
        if log_dir:
            log_plan_stage(log_dir, "parse_warn.txt", f"Strict parse failed:\n{e}\n\nRaw:\n{response_text}")

        # Try to extract first array block from the response
        cleaned = _extract_json_array(response_text)
        if not cleaned:
            if log_dir:
                log_plan_stage(log_dir, "parse_error.txt", f"Could not extract JSON array from:\n\n{response_text}")
            raise ValueError("Failed to extract JSON array from model output.")

        try:
            raw_steps = json.loads(cleaned)
            return _load_plan_steps(raw_steps)
        except Exception as e2:
            if log_dir:
                log_plan_stage(log_dir, "parse_error.txt", f"Cleaned parse failed:\n{e2}\n\nCleaned:\n{cleaned}")
            raise


def _extract_json_array(text: str) -> Optional[str]:
    """
    Extract JSON array from text that may contain markdown fences or prose.
    
    Uses regex to find the first occurrence of a JSON array pattern.
    
    Args:
        text: Input text that may contain a JSON array
        
    Returns:
        Extracted JSON array string, or None if not found
    """
    # Strip markdown fences and prose — return only the array block
    match = re.search(r"\[\s*{.*?}\s*\]", text, re.DOTALL)
    return match.group(0).strip() if match else None


def _load_plan_steps(raw_steps: List[dict]) -> List[PlanStep]:
    """
    Convert raw dictionary steps to validated PlanStep objects.
    
    Generates unique step IDs and ensures all required fields are present.
    
    Args:
        raw_steps: List of dictionaries from parsed JSON
        
    Returns:
        List of PlanStep objects with generated step IDs
    """
    return [
        PlanStep(
            step_id=str(uuid.uuid4()),
            description=step["description"],
            tool=step["tool"],
            args=step.get("args", {})
        )
        for step in raw_steps
    ] 