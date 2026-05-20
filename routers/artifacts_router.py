import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import pipeline and agent executors
from services.pipeline import run_full_pipeline
from agents.requirements_agent import run_requirements_agent
from agents.architecture_agent import run_architecture_agent
from agents.uml_agent import run_uml_agent
from agents.database_agent import run_database_agent
from agents.bootstrap_agent import run_bootstrap_agent

logger = logging.getLogger("artifacts_router")

router = APIRouter(tags=["Artifacts"])

# Pydantic input models
class RequirementsRequest(BaseModel):
    requirements: str

@router.post("/upload")
async def upload_requirements(file: UploadFile = File(...)):
    """
    Accepts text or markdown requirements file and extracts contents.
    """
    logger.info(f"Received file upload: {file.filename}")
    try:
        content_bytes = await file.read()
        try:
            content_text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content_text = content_bytes.decode("latin-1")
        
        return {
            "filename": file.filename,
            "content": content_text,
            "message": "Requirements file uploaded successfully"
        }
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

@router.post("/analyze/full")
async def analyze_full(request: RequirementsRequest):
    """
    Runs the full sequential multi-agent architecture analysis pipeline.
    """
    logger.info("Received POST /analyze/full request")
    if not request.requirements.strip():
        raise HTTPException(status_code=400, detail="Requirements text cannot be empty.")
    
    try:
        result = await run_full_pipeline(request.requirements)
        return result
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

@router.post("/analyze/uml")
async def analyze_uml(request: RequirementsRequest):
    """
    Runs UML Agent specifically by executing dependent preceding steps under the hood.
    """
    logger.info("Received POST /analyze/uml request")
    try:
        req_res = await run_requirements_agent(request.requirements)
        arch_res = await run_architecture_agent(req_res.get("data", {}))
        uml_res = await run_uml_agent(req_res.get("data", {}), arch_res.get("data", {}))
        return uml_res
    except Exception as e:
        logger.error(f"Error running UML Agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/database")
async def analyze_database(request: RequirementsRequest):
    """
    Runs Database Agent specifically by executing dependent preceding steps under the hood.
    """
    logger.info("Received POST /analyze/database request")
    try:
        req_res = await run_requirements_agent(request.requirements)
        arch_res = await run_architecture_agent(req_res.get("data", {}))
        uml_res = await run_uml_agent(req_res.get("data", {}), arch_res.get("data", {}))
        db_res = await run_database_agent(req_res.get("data", {}), uml_res.get("data", {}))
        return db_res
    except Exception as e:
        logger.error(f"Error running Database Agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/bootstrap")
async def analyze_bootstrap(request: RequirementsRequest):
    """
    Runs Bootstrap Agent specifically by executing dependent preceding steps under the hood.
    """
    logger.info("Received POST /analyze/bootstrap request")
    try:
        req_res = await run_requirements_agent(request.requirements)
        arch_res = await run_architecture_agent(req_res.get("data", {}))
        boot_res = await run_bootstrap_agent(req_res.get("data", {}), arch_res.get("data", {}))
        return boot_res
    except Exception as e:
        logger.error(f"Error running Bootstrap Agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/report")
async def download_report():
    """
    Serves the generated PDF report from the system temp directory
    """
    logger.info("Received GET /download/report request")
    pdf_path = os.path.join(tempfile.gettempdir(), "archgen_report.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=404, 
            detail="PDF Report not found. Please run a full analysis first to generate the report."
        )
    return FileResponse(
        path=pdf_path, 
        media_type="application/pdf", 
        filename="archgen_report.pdf"
    )
