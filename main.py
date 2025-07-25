"""
Site24x7 CLI AI Agent - Main Application
Autonomous GitHub project creation and maintenance for Site24x7 CLI
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import Settings
from database import init_db
from services.scheduler import SchedulerService
from routes.dashboard import router as dashboard_router
from routes.api import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('site24x7_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global scheduler_service
    
    # Startup
    logger.info("Starting Site24x7 CLI AI Agent...")
    
    # Initialize database
    init_db()
    
    # Initialize and start scheduler
    scheduler_service = SchedulerService()
    await scheduler_service.start()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Site24x7 CLI AI Agent...")
    if scheduler_service:
        await scheduler_service.shutdown()
    logger.info("Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Site24x7 CLI AI Agent",
    description="Autonomous GitHub project creation and maintenance for Site24x7 CLI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(dashboard_router, prefix="", tags=["dashboard"])
app.include_router(api_router, prefix="/api/v1", tags=["api"])

@app.get("/")
async def root(request: Request):
    """Root endpoint redirects to dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Site24x7 CLI AI Agent",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5545,
        reload=False,
        access_log=True
    )
