# planner/prompting.py
# LLM prompt generation utilities for tool examples and demonstrations.

import json
from typing import Dict, Any, Tuple
from spec.tool_specs import TOOL_SPECS


def build_example(tool: str) -> Dict[str, Any]:
    """
    Produce a minimal, valid example step for a specific tool.
    
    Generates realistic example arguments based on TOOL_SPECS by including
    all required arguments plus the first optional argument for realism.
    
    Args:
        tool: Tool name to generate example for
        
    Returns:
        Dictionary with example step structure including description, tool, and args
        
    Raises:
        KeyError: If tool is not found in TOOL_SPECS
    """
    spec = TOOL_SPECS[tool]
    args = {}

    # Example placeholders for each type
    _PLACEHOLDER = {
        "str": "<col>",
        "List[str]": ["<col>"],
        "float": 0.0,
        "int": 0,
        "bool": False,
    }

    for name, meta in spec.items():
        if meta["required"]:
            args[name] = _PLACEHOLDER.get(meta["type"], "<val>")
        elif not args:  # Include one optional for realism
            args[name] = _PLACEHOLDER.get(meta["type"], "<val>")

    return {
        "description": f"Example use of '{tool}'",
        "tool": tool,
        "args": args
    }


def build_example_block(tools: Tuple[str, ...] = ("summary_stats", "boxplot")) -> str:
    """
    Generate formatted JSON example block for LLM prompts.
    
    Creates a JSON array of example tool invocations to show the LLM
    the expected format and structure for plan steps.
    
    Args:
        tools: Tuple of tool names to include in examples
        
    Returns:
        Formatted JSON string ready for embedding in prompts
    """
    examples = [build_example(t) for t in tools]
    return json.dumps(examples, indent=2) 