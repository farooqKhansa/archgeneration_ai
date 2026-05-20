# 🚀 ArchGen AI - Multi-Agent Architecture Generation System

**Powered by Google Antigravity Managed Agents**

Transform software requirements into complete, production-ready architecture artifacts in minutes using AI agents.

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen) ![Google Antigravity](https://img.shields.io/badge/Google-Antigravity-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green) ![Python](https://img.shields.io/badge/Python-3.11-blue)

---

## 🎯 What is ArchGen AI?

**ArchGen AI** is an intelligent system that analyzes software requirements documents and generates complete architecture blueprints automatically using 7 specialized AI agents powered by Google Antigravity.

Upload a requirements PDF → Get architecture design, UML diagrams, database schema, and test cases in **15-20 seconds**.

### What You Get:
✅ **Requirements Analysis** - Actors, functional requirements, constraints extracted automatically  
✅ **Architecture Design** - Recommended patterns (Microservices, Monolith, etc.)  
✅ **UML Diagrams** - Use case, class, and sequence diagrams in Mermaid.js  
✅ **Database Schema** - Complete SQL design with ER diagrams  
✅ **Test Cases** - Unit, integration, and acceptance tests  
✅ **Project Bootstrap** - Simulated project structure generation  
✅ **PDF Reports** - Professional compilation of all artifacts  

---

## 🌍 Live Demo

**Try it now:**

- 📱 **Mobile App**: [Open in Expo](exp://exp.host/@farooqkhansa/archgen-app)
- 🌐 **Backend API**: [API Documentation](https://archgen-ai-backend.onrender.com/docs)
- 💻 **Health Check**: [Test Endpoint](https://archgen-ai-backend.onrender.com/health)

---

## ✨ Key Features

### 🤖 7 Intelligent Agents (5 Powered by Google Antigravity)

| # | Agent Name | Uses Antigravity | Purpose | Output Type |
|---|-----------|------------------|---------|-------------|
| 1 | Requirements Analysis | ✅ YES | Extract and structure requirements | JSON |
| 2 | Architecture Advisor | ✅ YES | Recommend design patterns | JSON |
| 3 | UML Generation | ✅ YES | Create visual diagrams | Mermaid Code |
| 4 | Database Design | ✅ YES | Design database schema | SQL + ER Diagram |
| 5 | Testing Agent | ✅ YES | Generate test cases | JSON |
| 6 | Project Bootstrap | ❌ Pure Python | Simulate project setup | Project Structure |
| 7 | Report Builder | ❌ PDF Generation | Compile artifacts | PDF File |

### 🎨 Multi-Platform Support

- 📱 **Mobile App**: React Native with Expo (iOS/Android/Web)
- 🌐 **Web Dashboard**: React with Vite (coming soon)
- 📊 **API**: RESTful with interactive Swagger documentation

### ⚡ Real-Time Processing

- Server-Sent Events (SSE) streaming for live updates
- Real-time agent progress tracking
- Instant result visualization

### 📦 Production Ready

- Cloud-deployed backend (Glitch/Heroku/Railway)
- Mobile app published (Expo)
- Complete error handling and fallback responses
- Execution tracing for transparency

---

## 🛠️ Technology Stack

### Backend
FastAPI 0.104          - Modern Python web framework
Python 3.11            - Latest Python version
Google Antigravity     - Managed AI agents (5 agents)
google-genai SDK       - Official Gemini API
PyMuPDF               - PDF text extraction
fpdf2                 - PDF report generation
Pydantic              - Data validation
uvicorn               - ASGI server
### Frontend
React Native 0.81     - Cross-platform mobile framework
Expo 54               - React Native development platform
React 19              - Web components (optional)
Axios                 - HTTP client
TypeScript            - Type safety
### Deployment & Infrastructure
Backend: Railway (Cloud)
Mobile:   Expo Publishing (OTA updates)
Database: Auto-generated SQL schemas
API:      RESTful with OpenAPI/Swagger
---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 16+ (for mobile app)
- Google Gemini API Key (free from aistudio.google.com)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/farooqKhansa/archgeneration_ai.git
cd archgeneration_ai
```

### 2️⃣ Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'ENVFILE'
GEMINI_API_KEY=your_api_key_here
ENVFILE

# Get API Key from: https://aistudio.google.com
```

### 3️⃣ Start Backend Server

```bash
python3 -m uvicorn main:app --reload --port 8000
```

**You should see:**
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete

### 4️⃣ Access Services
Interactive API Docs:   http://localhost:8000/docs
Alternative Docs:       http://localhost:8000/redoc
Health Check:          http://localhost:8000/health
OpenAPI Schema:        http://localhost:8000/openapi.json
### 5️⃣ Test the System

```bash
# Simple health check
curl http://localhost:8000/health

# Full analysis example
curl -X POST http://localhost:8000/analyze/full \
  -H "Content-Type: application/json" \
  -d '{"requirements": "E-commerce system with products, shopping cart, and payment processing"}'
```

---

## 📡 API Endpoints

### Upload Requirements File
```bash
POST /upload
Content-Type: multipart/form-data

curl -X POST http://localhost:8000/upload \
  -F "file=@requirements.pdf"

Response: {
  "filename": "requirements.pdf",
  "content": "Extracted text from PDF...",
  "message": "Requirements file uploaded successfully"
}
```

### Full Analysis Pipeline (Recommended)
```bash
POST /analyze/full
Content-Type: application/json

curl -X POST http://localhost:8000/analyze/full \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Your system requirements here"
  }'

Response: {
  "requirements": {...},
  "architecture": {...},
  "uml": {...},
  "database": {...},
  "test_cases": {...},
  "bootstrap": {...},
  "report": {...},
  "antigravity_trace": {
    "agents": [...],
    "total_duration_ms": 18000
  }
}
```

### Real-Time Agent Progress (SSE)
```bash
GET /analyze/stream?raw_text=<requirements>

# Live updates from agents
```

### Health Check
```bash
GET /health

Response: {"status": "ok", "antigravity": "connected"}
```

---

## 🤖 Google Antigravity Integration

This project uses 5 Google Antigravity Managed Agents:

1. **Requirements Agent** - Extracts and structures requirements
2. **Architecture Agent** - Recommends design patterns
3. **UML Agent** - Generates visual diagrams
4. **Database Agent** - Designs database schemas
5. **Testing Agent** - Creates test cases

Each agent uses the same pattern:
```python
from google import genai
client = genai.Client()
interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="your task",
    environment="remote",
)
result = interaction.output_text
```

---

## 🌍 Deployment

### Backend Deployment

**Glitch.com (Recommended)**
### Mobile App

```bash
cd frontend-mobile
npx expo publish
# Get link: exp://exp.host/@farooqkhansa/archgen-app
```

---

## 🏆 Google Antigravity Challenge 2026

### Submission Package:
- ✅ Mobile App (Expo)
- ✅ Backend (Cloud-deployed)
- ✅ GitHub Repository
- ✅ Demo Videos
- ✅ Documentation
- ✅ Antigravity Traces

### Links:
- **GitHub**: https://github.com/farooqKhansa/archgeneration_ai
- **Mobile App**: exp://exp.host/@farooqkhansa/archgen-app
- **Backend API**: https://archgen-ai-backend.onrender.com/docs

---

## 📄 License

MIT License - Open source and free to use

---

## 👥 Team

**Developer**: Khansa Farooq

**Built With**:
- 🤖 Google Antigravity
- ⚡ FastAPI
- 📱 React Native
- ☁️ Cloud Deployment

---

**Made with ❤️ for the Google Antigravity Challenge 2026**

⭐ **Star this repository if it helps you!**
