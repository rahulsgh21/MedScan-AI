from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import reports, chat
from app.core.config import settings
from app.utils.logger import get_logger
from app.core.db import engine, Base
from app.core.db_models import PatientReport

# Create DB tables
Base.metadata.create_all(bind=engine)

logger = get_logger(__name__)

def get_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for MedScan AI: Diagnostic Lab Report Translator"
    )

    # Configure CORS - important for React frontend
    # In production, specify the exact frontend origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for local development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
    
    @app.get("/health", tags=["health"])
    def read_health():
        return {"status": "ok", "app_name": settings.app_name, "version": settings.app_version}
        
    return app

app = get_application()

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.app_name} on http://0.0.0.0:8000")
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
