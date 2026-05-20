import os
import time
import logging
from typing import Dict, Any, Optional
from google import genai
from dotenv import load_dotenv

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("archgen_helpers")

# Load environment variables
load_dotenv()

# Initialize the Gemini API client safely
def get_genai_client() -> Optional[genai.Client]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set in environment. ArchGen AI will run in mock/fallback mode.")
        return None
    try:
        # Construct the Client. google-genai Client picks up api_key parameter or uses environment variables.
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}. Fallback mode will be used.")
        return None

# Predefined Fallback Mock Data for agents
FALLBACK_DATA = {
    "requirements_agent": {
        "actors": ["User", "System Administrator", "Stripe Payment Processor"],
        "functional_requirements": [
            "Users can browse, filter, and search software architecture blueprints.",
            "Users can input requirements and trigger sequential agent pipeline execution.",
            "System Administrators can monitor pipeline agent durations and execution trace logs.",
            "Users can download compiled 7-page PDF report summaries."
        ],
        "constraints": [
            "Every agent execution must be completed or fall back within 15 seconds.",
            "The system must programmatically validate generated Mermaid UML structures before output."
        ]
    },
    "architecture_agent": {
        "pattern": "Layered Architecture (N-Tier) with Orchestrated Services",
        "reasoning": "A layered architecture is highly structured and fits the sequential pipeline design of ArchGen AI perfectly. The API router handles requests, the service pipeline layer coordinates the agents, and the agents execute specialized functional tasks independently.",
        "components": [
            "Presentation Layer (FastAPI Routers handling HTTP POST / GET requests)",
            "Orchestration Service Layer (Sequential Pipeline coordinating AI and mock agent flows)",
            "Agent Integration Component (google-genai Client interfacing with Gemini-2.5-flash)",
            "Report Generation Component (FPDF2 utility outputting PDF reports)"
        ]
    },
    "testing_agent": {
        "test_cases": [
            {
                "id": "TC-REQ-001",
                "requirement": "Sequential multi-agent execution with duration tracking",
                "description": "Verify that all 7 agents execute in order and return their specific execution time (duration_ms).",
                "steps": [
                    "Prepare valid software requirements text input",
                    "Send POST request to /analyze/full",
                    "Verify the 'trace' list contains all 7 agent outcomes",
                    "Verify 'duration_ms' is present and > 0 for each entry"
                ],
                "expected_result": "Full pipeline response is returned with trace schema and valid durations."
            },
            {
                "id": "TC-REQ-002",
                "requirement": "Mermaid diagram code validation",
                "description": "Verify that generated UML diagrams and ER diagrams are verified against syntax rules before return.",
                "steps": [
                    "Send POST request to /analyze/uml",
                    "Assert that returned diagrams start with appropriate Mermaid headers ('graph', 'classDiagram', 'sequenceDiagram')"
                ],
                "expected_result": "Diagram outputs pass string pattern validation and return correct structure."
            }
        ]
    },
    "uml_agent": {
        "use_case_diagram": """graph TD
    User([User]) --> Browse[Browse Blueprints]
    User --> Trigger[Trigger Pipeline]
    User --> Download[Download PDF Report]
    Admin([System Admin]) --> Monitor[Monitor Trace Logs]
    Trigger --> Pipeline[Sequential Pipeline]
    Pipeline --> PDF[Generate Report]""",
        "class_diagram": """classDiagram
    class Agent {
        +string name
        +int duration_ms
        +dict data
        +execute(input) dict
    }
    class Pipeline {
        +list agents
        +run(requirements) dict
    }
    class ReportAgent {
        +generate_pdf(data) bytes
    }
    Pipeline *-- Agent
    Agent <|-- ReportAgent""",
        "sequence_diagram": """sequenceDiagram
    actor User
    participant Router as FastAPI Router
    participant Pipe as Pipeline Service
    participant ReqAgent as Requirements Agent
    participant Report as Report Agent

    User->>Router: POST /analyze/full
    Router->>Pipe: run_pipeline(requirements)
    Pipe->>ReqAgent: extract_requirements(requirements)
    ReqAgent-->>Pipe: requirements JSON
    Note over Pipe: Sequence through Arch, Test, UML, DB, Bootstrap
    Pipe->>Report: generate_report(all_data)
    Report-->>Pipe: pdf_path
    Pipe-->>Router: full JSON trace
    Router-->>User: returns full JSON trace"""
    },
    "database_agent": {
        "sql_schema": """CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pipeline_runs (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    requirements TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_traces (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    duration_ms INTEGER NOT NULL,
    agent_data JSONB NOT NULL
);""",
        "er_diagram": """erDiagram
    users ||--o{ pipeline_runs : initiates
    pipeline_runs ||--|{ agent_traces : logs"""
    }
}

async def generate_genai_content(
    prompt: str,
    agent_name: str,
    system_instruction: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates content using google-genai SDK with safety fallbacks.
    Returns the parsed JSON data or the agent's fallback structure.
    """
    client = get_genai_client()
    
    # If client is not configured, directly return fallback data
    if not client:
        logger.info(f"[{agent_name}] Running in mock/fallback mode (no client).")
        return FALLBACK_DATA.get(agent_name, {})

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    try:
        # Build configuration parameters
        config_params = {}
        if system_instruction:
            config_params["system_instruction"] = system_instruction
        
        # Request JSON output structure if possible
        config_params["response_mime_type"] = "application/json"
        
        # Set up timing
        start_time = time.perf_counter()
        
        # Use Client.models.generate_content
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config_params
        )
        
        # Parse the JSON response
        import json
        text = response.text
        # Clean response markdown wrapper blocks if the LLM output it
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()
        
        result = json.loads(text)
        logger.info(f"[{agent_name}] LLM generation succeeded.")
        return result
        
    except Exception as e:
        logger.error(f"[{agent_name}] Gemini API error: {e}. Falling back to default mock data.")
        return FALLBACK_DATA.get(agent_name, {})
