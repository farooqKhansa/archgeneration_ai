import time
import logging
from typing import Dict, Any
from utils.helpers import generate_genai_content, FALLBACK_DATA

logger = logging.getLogger("architecture_agent")

async def run_architecture_agent(requirements_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Architecture Agent: Suggests an architecture pattern (MVC / microservices / layered) and reasoning.
    """
    logger.info("Architecture Agent started execution.")
    start_time = time.perf_counter()
    
    prompt = f"""
    Given the following software requirements:
    Actors: {requirements_data.get('actors', [])}
    Functional Requirements: {requirements_data.get('functional_requirements', [])}
    Constraints: {requirements_data.get('constraints', [])}

    Determine the most appropriate software architectural pattern (e.g. Layered (N-Tier), Microservices, MVC, Event-Driven).
    Provide structural reasoning for this choice and list the key logical components or services.

    Return a JSON object with the following schema:
    {{
        "pattern": "string (the suggested pattern name)",
        "reasoning": "string (justifying the pattern choice based on constraints/requirements)",
        "components": ["string", ...]
    }}
    """
    
    system_instruction = "You are a senior software architect. Output only the requested JSON containing pattern, reasoning, and components."
    
    try:
        data = await generate_genai_content(
            prompt=prompt,
            agent_name="architecture_agent",
            system_instruction=system_instruction
        )
        if not isinstance(data, dict) or "pattern" not in data or "reasoning" not in data or "components" not in data:
            logger.warning("Architecture Agent response missing keys, merging with fallback.")
            fallback = FALLBACK_DATA["architecture_agent"]
            data = {
                "pattern": data.get("pattern", fallback["pattern"]) if isinstance(data, dict) else fallback["pattern"],
                "reasoning": data.get("reasoning", fallback["reasoning"]) if isinstance(data, dict) else fallback["reasoning"],
                "components": data.get("components", fallback["components"]) if isinstance(data, dict) else fallback["components"]
            }
    except Exception as e:
        logger.error(f"Architecture Agent error: {e}. Returning fallback data.")
        data = FALLBACK_DATA["architecture_agent"]

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"Architecture Agent completed execution in {duration_ms}ms.")
    
    return {
        "agent": "architecture_agent",
        "duration_ms": duration_ms,
        "data": data
    }
