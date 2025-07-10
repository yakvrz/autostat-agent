# planner/logging.py
# Logging utilities for plan generation and debugging.

import json
import uuid
import os
from typing import Any


class PlanLogger:
    """
    Create a run-specific log directory and dump text/JSON artifacts to it.
    
    Useful for debugging plan generation by capturing prompts, raw responses,
    and processed results in separate files.
    """
    
    def __init__(self, root: str = "logs"):
        """
        Initialize logger with a unique run ID.
        
        Args:
            root: Base directory for log storage
        """
        self.run_id = uuid.uuid4().hex
        self.dir = os.path.join(root, f"plan_{self.run_id}")
        os.makedirs(self.dir, exist_ok=True)

    def text(self, name: str, content: str) -> None:
        """
        Write text content to a .txt file.
        
        Args:
            name: Base filename (without extension)
            content: Text content to write
        """
        self._write(name, content, ".txt")

    def json(self, name: str, obj: Any) -> None:
        """
        Write object as formatted JSON to a .json file.
        
        Args:
            name: Base filename (without extension)  
            obj: Object to serialize as JSON
        """
        self._write(name, json.dumps(obj, indent=2), ".json")

    def _write(self, stem: str, payload: str, ext: str) -> None:
        """
        Internal method to write content to file.
        
        Args:
            stem: Base filename
            payload: Content to write
            ext: File extension
        """
        path = os.path.join(self.dir, f"{stem}{ext}")
        with open(path, "w") as f:
            f.write(payload)


def log_plan_stage(log_dir: str, filename: str, content: str) -> None:
    """
    Write content to a specific file in the log directory.
    
    Creates the directory if it doesn't exist. Useful for logging
    errors and warnings during plan parsing.
    
    Args:
        log_dir: Directory to write to
        filename: Name of the file to create
        content: Content to write
    """
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, filename)
    with open(path, "w") as f:
        f.write(content) 