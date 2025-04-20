from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="PM Agent",
    description="API for automating PM workflow—planning, risk check-ins, scheduling, alerts, logging, and reporting",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],  # Next.js & Streamlit URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Disposition"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to PM Agent API", "status": "operational"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

# Set up sys.path to find modules - following windsurf project structure
import sys
import os
from datetime import datetime

# Add current directory to path for proper module resolution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Function to log module loading to project_log.md
def log_module_load(module_name, success=True):
    # Only log successful loads to avoid cluttering the log
    if success:
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project_log.md"), "a") as log_file:
                timestamp = datetime.now().strftime("%Y‑%m‑%d %H:%M")
                log_file.write(f"- **{timestamp}**: Backend module loaded: {module_name}\n")
        except Exception as e:
            print(f"Warning: Could not write to project log: {e}")

# Import route handlers using relative imports - following windsurf naming conventions
try:
    from api.plan import router as plan_router
    app.include_router(plan_router, prefix="/api")
    print("✅ Plan API module loaded successfully")
    log_module_load("plan")
except ImportError as e:
    print(f"❌ Plan API module not found: {str(e)}")

try:
    from api.risk import router as risk_router
    app.include_router(risk_router, prefix="/api")
    print("✅ Risk API module loaded successfully")
    log_module_load("risk")
except ImportError as e:
    print(f"❌ Risk API module not found: {str(e)}")

try:
    from api.alerts import router as alerts_router
    app.include_router(alerts_router, prefix="/api")
    print("✅ Alerts API module loaded successfully")
    log_module_load("alerts")
except ImportError as e:
    print(f"❌ Alerts API module not found: {str(e)}")

try:
    from api.log import router as log_router
    app.include_router(log_router, prefix="/api")
    print("✅ Log API module loaded successfully")
    log_module_load("log")
except ImportError as e:
    print(f"❌ Log API module not found: {str(e)}")

try:
    from api.digest import router as digest_router
    app.include_router(digest_router, prefix="/api")
    print("✅ Digest API module loaded successfully") 
    log_module_load("digest")
except ImportError as e:
    print(f"❌ Digest API module not found: {str(e)}")

try:
    from api.schedule import router as schedule_router
    app.include_router(schedule_router, prefix="/api")
    print("✅ Schedule API module loaded successfully")
    log_module_load("schedule")
except ImportError as e:
    print(f"❌ Schedule API module not found: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
