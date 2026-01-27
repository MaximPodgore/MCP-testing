from typing import Optional
import requests
from langchain.tools import tool

from utils.skill import SKILLS

@tool
def load_skill(skill_name: str) -> str:
    """Load the full content of a skill into the agent's context.

    Use this when you need detailed information about how to handle a specific
    type of request. This will provide you with comprehensive instructions,
    policies, and guidelines for the skill area.

    Args:
        skill_name: The name of the skill to load (e.g., 'get-weather')
    
    Returns:
        The full skill content with instructions, or an error message if not found.
    """
    # Find and return the requested skill
    for skill in SKILLS:
        if skill["name"] == skill_name:
            return f"Loaded skill: {skill_name}\n\n{skill['content']}"

    # Skill not found
    available = ", ".join(s["name"] for s in SKILLS)
    return f"Skill '{skill_name}' not found. Available skills: {available}"

@tool
def curl(url: str, timeout_seconds: Optional[float] = 10.0) -> str:
    """HTTP GET a URL (e.g., wttr.in) and return the response text."""
    # Prepend https:// if caller omits scheme (matches skill examples)
    normalized = url if url.startswith(("http://", "https://")) else f"https://{url}"

    # Try HTTPS first, then fall back to HTTP if it times out (wttr.in allows both)
    schemes = [normalized]
    if normalized.startswith("https://"):
        schemes.append("http://" + normalized[len("https://"):])

    last_error = None
    for target in schemes:
        try:
            resp = requests.get(
                target,
                timeout=timeout_seconds or 20,
                headers={"User-Agent": "langgraph-skill-agent/1.0"},
            )
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException as exc:  # include timeouts
            last_error = exc
            continue

    # If all attempts fail, surface the last error
    raise last_error if last_error else RuntimeError("curl failed with no error captured")