"""
Prompt Builder for AI Insight Agent.
Loads the prompt template and injects structured context sections.
"""

from typing import Dict
from backend.services.llm_gateway import load_prompt
from .validators import validate_context_safety


class InsightPromptError(Exception):
    pass


def build_insight_prompt(context_dict: Dict[str, str]) -> str:
    """
    Build the final prompt string by injecting all 10 context sections
    into the template placeholders.
    """
    prompt_template = load_prompt("insight_prompt.txt")
    prompt = prompt_template.format(**context_dict)

    if not validate_context_safety(prompt):
        raise InsightPromptError(
            "Prompt validation failed: Unsafe or raw data detected in context."
        )

    return prompt
