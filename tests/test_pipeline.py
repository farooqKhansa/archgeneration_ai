import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    """Test standard home router endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ArchGen AI" in response.json()["message"]

def test_health():
    """Test health check router endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_full():
    """Test full sequential multi-agent architecture execution pipeline."""
    payload = {
        "requirements": "Build a secure medical appointment scheduling platform where patients can register, book appointments with doctors, and view prescription history."
    }
    response = client.post("/analyze/full", json=payload)
    assert response.status_code == 200
    
    res_data = response.json()
    assert res_data["status"] == "success"
    assert "total_duration_ms" in res_data
    assert "trace" in res_data
    
    traces = res_data["trace"]
    assert len(traces) == 7
    
    # Check that all agent traces are documented in the order they ran
    expected_agents = [
        "requirements_agent",
        "architecture_agent",
        "testing_agent",
        "uml_agent",
        "database_agent",
        "bootstrap_agent",
        "report_agent"
    ]
    for idx, agent_name in enumerate(expected_agents):
        assert traces[idx]["agent"] == agent_name
        assert "duration_ms" in traces[idx]
        assert "data" in traces[idx]

    # Verify that PDF was created
    pdf_path = os.path.join(tempfile.gettempdir(), "archgen_report.pdf")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

def test_analyze_uml():
    """Test standalone UML analysis endpoint."""
    payload = {
        "requirements": "E-commerce checkout system"
    }
    response = client.post("/analyze/uml", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "uml_agent"
    assert "use_case_diagram" in data["data"]
    assert "class_diagram" in data["data"]
    assert "sequence_diagram" in data["data"]

def test_analyze_database():
    """Test standalone Database analysis endpoint."""
    payload = {
        "requirements": "Blog platform with posts and comments"
    }
    response = client.post("/analyze/database", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "database_agent"
    assert "sql_schema" in data["data"]
    assert "er_diagram" in data["data"]

def test_analyze_bootstrap():
    """Test standalone Bootstrap analysis endpoint."""
    payload = {
        "requirements": "Recipe sharing web app"
    }
    response = client.post("/analyze/bootstrap", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "bootstrap_agent"
    assert "folder_structure" in data["data"]
    assert "config_files" in data["data"]
    assert "mock_db_logs" in data["data"]
    assert "task_board" in data["data"]

def test_download_report():
    """Test download endpoint returns PDF data."""
    # Delete report first to ensure download fails, run full pipeline to create, and check download succeeds
    pdf_path = os.path.join(tempfile.gettempdir(), "archgen_report.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    response = client.get("/download/report")
    assert response.status_code == 404

    # Generate report
    payload = {"requirements": "A simple API project"}
    client.post("/analyze/full", json=payload)

    # Try downloading again
    response = client.get("/download/report")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0
