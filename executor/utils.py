# executor/utils.py
# Argument validation and coercion utilities for tool execution.

from typing import Any, Dict, List, Tuple, Optional, Set, Sequence
from spec.tool_specs import TOOL_SPECS

def _to_list(val: Any) -> List[str]:
    """Return a flat list of strings from str, Sequence, ndarray, etc."""
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    if isinstance(val, Sequence):
        # Flatten one-level and cast to str
        return [str(x) for x in val]
    # Fallback: wrap scalar
    return [str(val)]

def coerce_args(tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform `args` so they conform to the expected shapes in TOOL_SPECS:
        • List[str]  ← str           (wrap)
        • List[str]  ← list/tuple    (cast items to str)
        • str        ← list[str] len==1 (unwrap)
        • str        ← anything else via str()
    Unknown keys are passed through unchanged.
    """
    spec = TOOL_SPECS.get(tool, {})
    coerced: Dict[str, Any] = {}

    for key, val in args.items():
        expected_type = spec.get(key, {}).get("type")

        # Handle list[str] expectations
        if expected_type == "List[str]":
            coerced[key] = _to_list(val)

        # Handle str expectations
        elif expected_type == "str":
            if isinstance(val, (list, tuple)) and len(val) == 1:
                coerced[key] = str(val[0])
            else:
                coerced[key] = str(val)

        # Pass through undeclared arguments
        else:
            coerced[key] = val

    return coerced

def validate_args(tool_name: str, args: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Return (valid: bool, error_msg: Optional[str]).
    Does *key* validation only – type checks are executor-level.
    """
    spec = TOOL_SPECS.get(tool_name)
    if spec is None:
        return False, f"Unknown tool '{tool_name}'."

    # Check required keys
    for arg, meta in spec.items():
        if meta["required"] and arg not in args:
            return False, f"Missing required arg '{arg}' for tool '{tool_name}'."

    # Check for unexpected arguments
    extra: Set[str] = set(args).difference(spec.keys())
    if extra:
        return False, f"Unexpected arg(s) {sorted(extra)} for tool '{tool_name}'."

    return True, None