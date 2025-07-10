# planner/llm_planner.py
# Primary LLM-based planner to break down high-level prompts into actionable steps.

import requests
import json
from typing import List
from importlib.resources import files
from core.state import PromptState
from planner.schemas import PlanStep
from planner.parsing import parse_plan
from planner.processing import deduplicate_steps
from planner.prompting import build_example_block
from planner.logging import PlanLogger
from spec.tool_specs import TOOL_SPECS, get_tool_schema_block

# Constants
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "gemma3:12b"
OLLAMA_GENERATE_ENDPOINT = "/api/generate"


def plan(prompt_state: PromptState) -> List[PlanStep]:
    """
    Generate a structured plan from a user's research question.
    
    Args:
        prompt_state: Contains the user's question, dataset profile, and context
        
    Returns:
        List of validated and deduplicated plan steps
    """
    prompt = build_prompt(prompt_state)
    response_txt = call_ollama(prompt)

    logger = PlanLogger()

    logger.text("prompt", prompt)
    logger.text("raw", response_txt)

    steps = parse_plan(response_txt, log_dir=logger.dir)
    logger.json("clean", [s.model_dump() for s in steps])

    steps = deduplicate_steps(steps)
    logger.json("dedup", [s.model_dump() for s in steps])

    return steps


def call_ollama(prompt: str) -> str:
    """
    Send a prompt to the local Ollama instance and return the response.
    
    Args:
        prompt: The formatted prompt string to send
        
    Returns:
        The raw text response from the model
        
    Raises:
        requests.HTTPError: If the API call fails
        KeyError: If response format is unexpected
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(f"{OLLAMA_HOST}{OLLAMA_GENERATE_ENDPOINT}", json=payload)
    response.raise_for_status()
    return response.json()["response"]


def _get_prompt_template() -> str:
    """
    Reads the system prompt template from the prompts directory.
    
    Returns:
        The prompt template as a string
    """
    path = files("planner.prompts").joinpath("system.prompt")
    return path.read_text()


def build_prompt(prompt_state: PromptState) -> str:
    """
    Build the complete prompt by filling the template with context.
    
    Args:
        prompt_state: Contains question, profile, and other context
        
    Returns:
        The formatted prompt ready for the LLM
    """
    template = _get_prompt_template()

    return template.format(
        schema_block=get_tool_schema_block(),
        example_block=build_example_block(),
        question=prompt_state.question,
        profile_json=json.dumps(prompt_state.profile, indent=2),
    ).strip()