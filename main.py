import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.artifacts_router import router as artifacts_router
from dotenv import load_dotenv

# Load env variables on startup
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

app = FastAPI(
    title="ArchGen AI",
    description="A multi-agent system to convert software requirements into architectural artifacts",
    version="1.0.0"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register artifacts router
app.include_router(artifacts_router)

@app.get("/")
def home():
    return {"message": "🚀 ArchGen AI backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Redeployment fix
