# spec/tool_specs.py
# Single source-of-truth for all tool argument schemas.
# Ensures the planner, validator and executor components stay synchronized.

from __future__ import annotations
from typing import Dict, Any

# Tool argument metadata structure
ToolArgMeta = Dict[str, Any]  # Contains: {"type": str, "required": bool, "description": str}
ToolSpec = Dict[str, ToolArgMeta]
ToolSpecRegistry = Dict[str, ToolSpec]

# Hard-coded specification for all available tools
# Format: {tool_name: {arg_name: {"type": str, "required": bool, "description": str}}}
TOOL_SPECS: ToolSpecRegistry = {
    "eda_overview": {},  # No arguments required

    "summary_stats": {
        "columns": {
            "type": "List[str]",
            "required": True,
            "description": "Numeric columns to summarise",
        },
        "by": {
            "type": "str",
            "required": False,
            "description": "Single grouping column (do NOT supply a list)",
        },
    },

    "boxplot": {
        "x": {
            "type": "str",
            "required": True,
            "description": "Grouping / category column (plotted on the x-axis)",
        },
        "y": {
            "type": "str",
            "required": True,
            "description": "Numeric column whose distribution is plotted on the y-axis",
        },
    },

    "histogram": {
        "columns": {
            "type": "List[str]",
            "required": True,
            "description": "Numeric columns to plot",
        },
    },

    "t_test": {
        "group_column": {
            "type": "str",
            "required": True,
            "description": "Grouping variable (2 levels)",
        },
        "value_column": {
            "type": "str",
            "required": True,
            "description": "Numeric outcome to compare",
        },
    },
}


def _spec_line(name: str, spec: ToolSpec) -> str:
    """
    Render one tool specification as a single formatted line.
    
    Args:
        name: Tool name
        spec: Tool specification with argument metadata
        
    Returns:
        Formatted string showing tool name and arguments
    """
    if not spec:
        return f"- {name}: {{}}"
    
    parts = []
    for arg, meta in spec.items():
        req_status = "required" if meta["required"] else "optional"
        parts.append(f"{arg}[{meta['type']}] ({req_status})")
    
    return f"- {name}: " + ", ".join(parts)


def get_tool_schema_block() -> str:
    """
    Generate a multi-line string representation of all tool specifications.
    
    This format is suitable for embedding in LLM prompts to inform the
    model about available tools and their argument requirements.
    
    Returns:
        Formatted string with all tool specifications
    """
    lines = ["TOOL SPECIFICATION (strict):"]
    for tool_name, spec in TOOL_SPECS.items():
        lines.append("  " + _spec_line(tool_name, spec))
    return "\n".join(lines)

