"""Main FastAPI application"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.config import settings
from app.db import init_db

# Import all models to register them with SQLModel metadata
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
from app.api.organizations import router as org_router
from app.api.asset_types import router as asset_types_router
from app.api.work_items import router as work_items_router
from app.api.dashboard import router as dashboard_router

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

# Mount static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup Jinja2 templates
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Include routers
app.include_router(auth_router)
app.include_router(org_router)
app.include_router(asset_types_router)
app.include_router(work_items_router)
app.include_router(dashboard_router)


# Serve HTML pages
@app.get("/login")
def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    """Serve registration page"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard")
def dashboard_page(request: Request):
    """Serve dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/locations")
def locations_page(request: Request):
    """Serve locations page"""
    return templates.TemplateResponse("locations.html", {"request": request})


@app.get("/work-items")
def work_items_page(request: Request):
    """Serve work items page"""
    return templates.TemplateResponse("work-items.html", {"request": request})


@app.get("/settings")
def settings_page(request: Request):
    """Serve settings page"""
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.app_env}


@app.get("/")
def root(request: Request):
    """Root endpoint - redirect to login or dashboard"""
    return templates.TemplateResponse("login.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
