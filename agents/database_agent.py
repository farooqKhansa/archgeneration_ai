import time
import logging
from typing import Dict, Any
from utils.helpers import generate_genai_content, FALLBACK_DATA

logger = logging.getLogger("database_agent")

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

def validate_er_diagram(diagram: str) -> bool:
    cleaned = clean_mermaid_code(diagram)
    return cleaned.startswith("erDiagram")

async def run_database_agent(requirements_data: Dict[str, Any], uml_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Database Agent: Generates SQL Schema and ER diagram (Mermaid format).
    Validates ER diagram starts with 'erDiagram'.
    """
    logger.info("Database Agent started execution.")
    start_time = time.perf_counter()
    
    prompt = f"""
    Given the following software requirements and UML class design:
    Functional Requirements: {requirements_data.get('functional_requirements', [])}
    Class Diagram Structure: {uml_data.get('class_diagram', '')}

    Generate a relational database schema:
    1. SQL Schema: DDL statements with primary keys, foreign keys, constraints, and data types (PostgreSQL style).
    2. ER Diagram: Mermaid erDiagram code representing entities, primary/foreign key attributes, and relationship cardinalities.

    Return a JSON object with the following schema:
    {{
        "sql_schema": "string (raw SQL CREATE TABLE scripts)",
        "er_diagram": "string (raw Mermaid code starting with erDiagram)"
    }}
    """
    
    system_instruction = "You are a senior database engineer. Generate SQL and Mermaid ER diagrams. Output only the requested JSON containing sql_schema and er_diagram."
    
    try:
        data = await generate_genai_content(
            prompt=prompt,
            agent_name="database_agent",
            system_instruction=system_instruction
        )
        
        fallback = FALLBACK_DATA["database_agent"]
        
        # Clean and validate SQL Schema
        sql = data.get("sql_schema", "")
        
        # Clean and validate ER Diagram
        er = data.get("er_diagram", "")
        if not validate_er_diagram(er):
            logger.warning("ER Diagram failed validation. Reverting to fallback.")
            er = fallback["er_diagram"]
        else:
            er = clean_mermaid_code(er)
            
        data = {
            "sql_schema": sql,
            "er_diagram": er
        }
    except Exception as e:
        logger.error(f"Database Agent error: {e}. Returning fallback data.")
        data = FALLBACK_DATA["database_agent"]

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"Database Agent completed execution in {duration_ms}ms.")
    
    return {
        "agent": "database_agent",
        "duration_ms": duration_ms,
        "data": data
    }
