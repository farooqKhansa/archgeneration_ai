import time
import logging
from typing import Dict, Any
from utils.helpers import generate_genai_content, FALLBACK_DATA

logger = logging.getLogger("requirements_agent")

async def run_requirements_agent(requirements_text: str) -> Dict[str, Any]:
    """
    Requirements Agent: Extracts actors, functional requirements, and constraints.
    """
    logger.info("Requirements Agent started execution.")
    start_time = time.perf_counter()
    
    prompt = f"""
    Analyze the following software requirements text and extract:
    1. Actors: Users, roles, or external systems interacting with the system.
    2. Functional Requirements: Core functionalities and features the system must provide.
    3. Constraints: Non-functional constraints, technical limitations, security rules, or performance targets.

    Input Requirements:
    {requirements_text}

    Return a JSON object with the following schema:
    {{
        "actors": ["string", ...],
        "functional_requirements": ["string", ...],
        "constraints": ["string", ...]
    }}
    """
    
    system_instruction = "You are a professional system analyst. Output only the requested JSON containing actors, functional_requirements, and constraints."
    
    try:
        data = await generate_genai_content(
            prompt=prompt,
            agent_name="requirements_agent",
            system_instruction=system_instruction
        )
        # Ensure schema structure exists
        if not isinstance(data, dict) or "actors" not in data or "functional_requirements" not in data or "constraints" not in data:
            logger.warning("Requirements Agent response missing keys, merging with fallback.")
            fallback = FALLBACK_DATA["requirements_agent"]
            data = {
                "actors": data.get("actors", fallback["actors"]) if isinstance(data, dict) else fallback["actors"],
                "functional_requirements": data.get("functional_requirements", fallback["functional_requirements"]) if isinstance(data, dict) else fallback["functional_requirements"],
                "constraints": data.get("constraints", fallback["constraints"]) if isinstance(data, dict) else fallback["constraints"]
            }
    except Exception as e:
        logger.error(f"Requirements Agent error: {e}. Returning fallback data.")
        data = FALLBACK_DATA["requirements_agent"]

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"Requirements Agent completed execution in {duration_ms}ms.")
    
    return {
        "agent": "requirements_agent",
        "duration_ms": duration_ms,
        "data": data
    }
