"""Main Flask application"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
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

# Import API blueprints
from app.api.auth import auth_bp
from app.api.organizations import org_bp
from app.api.asset_types import asset_types_bp
from app.api.work_items import work_items_bp
from app.api.dashboard import dashboard_bp

# Initialize database
init_db()

# Create Flask app
templates_path = Path(__file__).parent.parent / "templates"
static_path = Path(__file__).parent.parent / "static"

app = Flask(
    __name__,
    template_folder=str(templates_path),
    static_folder=str(static_path),
)

app.config["SECRET_KEY"] = settings.secret_key
app.config["DEBUG"] = settings.debug

# Add CORS
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(org_bp)
app.register_blueprint(asset_types_bp)
app.register_blueprint(work_items_bp)
app.register_blueprint(dashboard_bp)


# Serve HTML pages
@app.route("/login")
def login_page():
    """Serve login page"""
    return render_template("login.html")


@app.route("/register")
def register_page():
    """Serve registration page"""
    return render_template("register.html")


@app.route("/dashboard")
def dashboard_page():
    """Serve dashboard page"""
    return render_template("dashboard.html")


@app.route("/locations")
def locations_page():
    """Serve locations page"""
    return render_template("locations.html")


@app.route("/assets")
def assets_page():
    """Serve assets page"""
    return render_template("assets.html")


@app.route("/work-items")
def work_items_page():
    """Serve work items page"""
    return render_template("work-items.html")


@app.route("/settings")
def settings_page():
    """Serve settings page"""
    return render_template("settings.html")


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "environment": settings.app_env})


@app.route("/")
def root():
    """Root endpoint - redirect to login or dashboard"""
    return render_template("login.html")


if __name__ == "__main__":
    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.reload,
    )
