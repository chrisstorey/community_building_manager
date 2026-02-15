"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import init_db

# Import all models to register them with Base
from app.models.user import User  # noqa: F401
from app.models.organization import (  # noqa: F401
    Organization,
    KeyContact,
    Location,
    LocationType,
    LocationAsset,
)
from app.models.work import WorkArea, WorkItem, Update  # noqa: F401

# Import API routers
from app.api.auth import router as auth_router

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Service for managing community buildings and activities",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.app_env}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Community Building Manager API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
