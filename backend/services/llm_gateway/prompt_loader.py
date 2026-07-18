"""
Utility for safely loading prompt templates from the filesystem.
"""

from pathlib import Path
from backend.utils.logger import logger


def load_prompt(prompt_name: str) -> str:
    """
    Loads a prompt from a text/markdown file in backend/prompts/.

    Args:
        prompt_name: The filename of the prompt (e.g., 'planner_prompt.txt').

    Returns:
        The content of the prompt file.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    # Resolves to e:/GIT PROJECTS/FinTech/backend/prompts/
    base_dir = Path(__file__).resolve().parent.parent.parent
    prompt_path = base_dir / "prompts" / prompt_name

    if not prompt_path.exists():
        logger.error(f"Prompt file not found: {prompt_path}")
        raise FileNotFoundError(
            f"Prompt file {prompt_name} does not exist in {base_dir}/prompts/"
        )

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
