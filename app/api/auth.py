"""Authentication routes"""
from datetime import timedelta
from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError

from app.db import get_session
from app.schemas.auth import LoginRequest, UserCreate
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_current_user, require_auth
from app.services.user_service import get_user_by_email, create_user
from app.config import settings

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login with email and password"""
    try:
        data = request.get_json()
        credentials = LoginRequest(**data)
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    user = get_user_by_email(db, credentials.email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        return jsonify({"detail": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"detail": "User account is inactive"}), 403

    access_token = create_access_token(
        data={"sub": str(user.id), "org_id": user.organization_id},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return jsonify({"access_token": access_token, "token_type": "bearer"}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        user_data = UserCreate(**data)
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        return jsonify({"detail": "Email already registered"}), 409

    db_user = create_user(db, user_data)
    return jsonify({
        "id": db_user.id,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "role": db_user.role,
        "organization_id": db_user.organization_id,
    }), 201


@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_me():
    """Get current user information"""
    current_user = get_current_user()
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "organization_id": current_user.organization_id,
    }), 200
