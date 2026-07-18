"""
Service layer for the Planner Agent.
Handles LLM invocation, prompt formatting, and prompt versioning.
"""
import hashlib
from typing import Dict, Any, Tuple, Optional
from backend.services.llm_gateway import llm_gateway, load_prompt
from .planner_models import PlannerOutput
from backend.utils.logger import logger

def _create_planner_prompt(summary: Dict[str, str], domain_hint: str) -> Tuple[str, str, str]:
    prompt_template = load_prompt("planner_prompt.txt")
    prompt = prompt_template.format(domain_hint=domain_hint, **summary)
    
    prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    prompt_version = "v2.0" # Hardcoded metadata for prompt versioning
    
    return prompt, prompt_version, prompt_hash

def invoke_planner_llm(summary: Dict[str, str], domain_hint: str) -> Tuple[Optional[Any], str, str]:
    prompt, p_version, p_hash = _create_planner_prompt(summary, domain_hint)
    
    try:
        response = llm_gateway.invoke_structured(
            prompt=prompt,
            output_schema=PlannerOutput,
            calling_agent="Planner Agent",
            temperature=0.1
        )
        return response, p_version, p_hash
    except Exception as e:
        logger.error(f"Planner LLM failed: {str(e)}")
        return None, p_version, p_hash
