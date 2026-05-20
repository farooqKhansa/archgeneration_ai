import time
import logging
from typing import Dict, Any, List

# Import agents
from agents.requirements_agent import run_requirements_agent
from agents.architecture_agent import run_architecture_agent
from agents.testing_agent import run_testing_agent
from agents.uml_agent import run_uml_agent
from agents.database_agent import run_database_agent
from agents.bootstrap_agent import run_bootstrap_agent
from agents.report_agent import run_report_agent

logger = logging.getLogger("pipeline_service")

async def run_full_pipeline(requirements_text: str) -> Dict[str, Any]:
    """
    Runs the sequential multi-agent architecture analysis pipeline.
    Pipeline Flow: User Input -> Requirements -> Architecture -> Testing -> UML -> Database -> Bootstrap -> Report
    """
    logger.info("Starting ArchGen AI Sequential Pipeline execution.")
    pipeline_start = time.perf_counter()
    
    trace_logs: List[Dict[str, Any]] = []
    
    # 1. Requirements Agent
    req_result = await run_requirements_agent(requirements_text)
    trace_logs.append(req_result)
    req_data = req_result.get("data", {})
    
    # 2. Architecture Agent
    arch_result = await run_architecture_agent(req_data)
    trace_logs.append(arch_result)
    arch_data = arch_result.get("data", {})
    
    # 3. Testing Agent
    test_result = await run_testing_agent(req_data, arch_data)
    trace_logs.append(test_result)
    
    # 4. UML Agent
    uml_result = await run_uml_agent(req_data, arch_data)
    trace_logs.append(uml_result)
    uml_data = uml_result.get("data", {})
    
    # 5. Database Agent
    db_result = await run_database_agent(req_data, uml_data)
    trace_logs.append(db_result)
    
    # 6. Bootstrap Agent
    boot_result = await run_bootstrap_agent(req_data, arch_data)
    trace_logs.append(boot_result)
    
    # Prepare intermediate payload for Report Agent compile
    pipeline_results = {
        "trace": trace_logs
    }
    
    # 7. Report Agent
    report_result = await run_report_agent(pipeline_results)
    trace_logs.append(report_result)
    
    pipeline_duration_ms = int((time.perf_counter() - pipeline_start) * 1000)
    logger.info(f"Pipeline execution completed in {pipeline_duration_ms}ms.")
    
    return {
        "status": "success",
        "total_duration_ms": pipeline_duration_ms,
        "trace": trace_logs
    }
