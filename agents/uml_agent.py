import time
import logging
from typing import Dict, Any
from utils.helpers import generate_genai_content, FALLBACK_DATA

logger = logging.getLogger("uml_agent")

def clean_mermaid_code(code: str) -> str:
    """
    Cleans markdown wrappers and trailing whitespaces around Mermaid code.
    """
    if not code:
        return ""
    cleaned = code.strip()
    if cleaned.startswith("```mermaid"):
        cleaned = cleaned.replace("```mermaid", "", 1)
    elif cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1)
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return cleaned.strip()

def validate_use_case_diagram(diagram: str) -> bool:
    cleaned = clean_mermaid_code(diagram)
    # Flowcharts or graphs are standard for use cases in Mermaid
    return any(cleaned.startswith(kw) for kw in ["graph", "flowchart"])

def validate_class_diagram(diagram: str) -> bool:
    cleaned = clean_mermaid_code(diagram)
    return cleaned.startswith("classDiagram")

def validate_sequence_diagram(diagram: str) -> bool:
    cleaned = clean_mermaid_code(diagram)
    return cleaned.startswith("sequenceDiagram")

async def run_uml_agent(requirements_data: Dict[str, Any], architecture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    UML Agent: Generates use case, class, and sequence diagrams.
    Validates that each diagram starts with correct Mermaid keywords.
    """
    logger.info("UML Agent started execution.")
    start_time = time.perf_counter()
    
    prompt = f"""
    Given the following software requirements and architectural design:
    Functional Requirements: {requirements_data.get('functional_requirements', [])}
    Architecture Pattern: {architecture_data.get('pattern', '')}

    Generate three distinct Mermaid diagrams:
    1. Use Case Diagram: Model actors interacting with system boundaries (Must use 'graph' or 'flowchart' keyword).
    2. Class Diagram: Define key logical domain objects, their properties, methods, and relations (Must use 'classDiagram' keyword).
    3. Sequence Diagram: Show interactions over time between actors and components during a critical execution flow (Must use 'sequenceDiagram' keyword).

    Return a JSON object with the following schema:
    {{
        "use_case_diagram": "string (raw Mermaid code starting with graph or flowchart)",
        "class_diagram": "string (raw Mermaid code starting with classDiagram)",
        "sequence_diagram": "string (raw Mermaid code starting with sequenceDiagram)"
    }}
    """
    
    system_instruction = "You are a software design agent. Generate valid Mermaid diagrams. Output only the requested JSON containing use_case_diagram, class_diagram, and sequence_diagram."
    
    try:
        data = await generate_genai_content(
            prompt=prompt,
            agent_name="uml_agent",
            system_instruction=system_instruction
        )
        
        fallback = FALLBACK_DATA["uml_agent"]
        
        # Clean and validate Use Case Diagram
        use_case = data.get("use_case_diagram", "")
        if not validate_use_case_diagram(use_case):
            logger.warning("Use Case Diagram failed validation. Reverting to fallback.")
            use_case = fallback["use_case_diagram"]
        else:
            use_case = clean_mermaid_code(use_case)
            
        # Clean and validate Class Diagram
        class_diag = data.get("class_diagram", "")
        if not validate_class_diagram(class_diag):
            logger.warning("Class Diagram failed validation. Reverting to fallback.")
            class_diag = fallback["class_diagram"]
        else:
            class_diag = clean_mermaid_code(class_diag)
            
        # Clean and validate Sequence Diagram
        seq_diag = data.get("sequence_diagram", "")
        if not validate_sequence_diagram(seq_diag):
            logger.warning("Sequence Diagram failed validation. Reverting to fallback.")
            seq_diag = fallback["sequence_diagram"]
        else:
            seq_diag = clean_mermaid_code(seq_diag)
            
        data = {
            "use_case_diagram": use_case,
            "class_diagram": class_diag,
            "sequence_diagram": seq_diag
        }
    except Exception as e:
        logger.error(f"UML Agent error: {e}. Returning fallback data.")
        data = FALLBACK_DATA["uml_agent"]

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"UML Agent completed execution in {duration_ms}ms.")
    
    return {
        "agent": "uml_agent",
        "duration_ms": duration_ms,
        "data": data
    }
