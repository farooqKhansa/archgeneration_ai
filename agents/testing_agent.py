import time
import logging
from typing import Dict, Any
from utils.helpers import generate_genai_content, FALLBACK_DATA

logger = logging.getLogger("testing_agent")

async def run_testing_agent(requirements_data: Dict[str, Any], architecture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Testing Agent: Generates test cases mapped to functional requirements.
    """
    logger.info("Testing Agent started execution.")
    start_time = time.perf_counter()
    
    prompt = f"""
    Given the following software requirements and architectural design:
    Functional Requirements: {requirements_data.get('functional_requirements', [])}
    Architecture Pattern: {architecture_data.get('pattern', '')}

    Generate a comprehensive set of test cases to verify these requirements.
    Each test case must map to a specific functional requirement.

    Return a JSON object with the following schema:
    {{
        "test_cases": [
            {{
                "id": "string (e.g. TC-001)",
                "requirement": "string (the exact requirement verified)",
                "description": "string (what is tested)",
                "steps": ["string", ...],
                "expected_result": "string (what the expected behavior is)"
            }},
            ...
        ]
    }}
    """
    
    system_instruction = "You are a professional QA engineer. Output only the requested JSON containing test_cases list."
    
    try:
        data = await generate_genai_content(
            prompt=prompt,
            agent_name="testing_agent",
            system_instruction=system_instruction
        )
        if not isinstance(data, dict) or "test_cases" not in data:
            logger.warning("Testing Agent response missing keys, merging with fallback.")
            fallback = FALLBACK_DATA["testing_agent"]
            data = {
                "test_cases": data.get("test_cases", fallback["test_cases"]) if isinstance(data, dict) else fallback["test_cases"]
            }
    except Exception as e:
        logger.error(f"Testing Agent error: {e}. Returning fallback data.")
        data = FALLBACK_DATA["testing_agent"]

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"Testing Agent completed execution in {duration_ms}ms.")
    
    return {
        "agent": "testing_agent",
        "duration_ms": duration_ms,
        "data": data
    }
