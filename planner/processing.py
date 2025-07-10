# planner/processing.py
# Plan post-processing utilities for deduplication and normalization.

import json
from typing import List, Any, Union
from planner.schemas import PlanStep


def deduplicate_steps(steps: List[PlanStep]) -> List[PlanStep]:
    """
    Remove duplicate plan steps based on their tool and normalized arguments.
    
    Steps are considered duplicates if their tool and arguments (after normalization)
    are identical. This prevents redundant analysis steps in the generated plan.
    
    Args:
        steps: List of plan steps to deduplicate
        
    Returns:
        List of unique plan steps, preserving original order
    """
    seen = set()
    deduped = []
    
    for step in steps:
        norm_args = _normalize_args(step.args)
        # Create a unique signature for each step using tool and normalized args
        sig = (step.tool, json.dumps(norm_args, sort_keys=True))
        if sig not in seen:
            seen.add(sig)
            deduped.append(step)
            
    return deduped


def _normalize_args(value: Any) -> Any:
    """
    Recursively normalize arguments for comparison.
    
    Ensures that argument order does not affect deduplication by:
    - Sorting dictionary keys
    - Sorting lists  
    - Leaving primitive values unchanged
    
    Args:
        value: Value to normalize (can be dict, list, or primitive)
        
    Returns:
        Normalized value suitable for comparison
    """
    if isinstance(value, dict):
        return {k: _normalize_args(value[k]) for k in sorted(value)}
    elif isinstance(value, list):
        return sorted(_normalize_args(v) for v in value)
    else:
        return value 