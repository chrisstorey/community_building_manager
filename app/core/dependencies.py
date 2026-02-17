"""Flask dependencies and utilities"""
from functools import wraps
from flask import request, jsonify, g
from sqlmodel import Session

from app.core.security import decode_token
from app.db import get_session
from app.models.user import User, UserRole
from app.services.user_service import get_user_by_id


def get_token_from_request() -> str | None:
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        # Expected format: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
    except Exception:
        pass

    return None


def get_current_user() -> User | None:
    """Get current authenticated user from request context"""
    if "current_user" in g:
        return g.current_user

    token = get_token_from_request()
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    db = get_session()
    user = get_user_by_id(db, int(user_id))

    if not user or not user.is_active:
        return None

    g.current_user = user
    return user


def require_auth(f):
    """Decorator for endpoints requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Invalid authentication credentials"}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator for admin-only endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Invalid authentication credentials"}), 401
        if user.role != UserRole.ADMIN:
            return jsonify({"detail": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


def require_manager(f):
    """Decorator for manager and admin endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Invalid authentication credentials"}), 401
        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            return jsonify({"detail": "Manager access required"}), 403
        return f(*args, **kwargs)
    return decorated_function
