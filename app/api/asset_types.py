"""Asset type management routes"""
from flask import Blueprint, request, jsonify
from sqlmodel import select
from pydantic import ValidationError

from app.db import get_session
from app.models.organization import LocationType
from app.core.dependencies import require_admin, require_auth
from app.schemas.organization import LocationTypeCreate
from app.services.organization_service import (
    create_location_type,
    get_location_type_by_id,
    get_all_location_types,
    initialize_default_asset_types,
)

asset_types_bp = Blueprint("asset_types", __name__, url_prefix="/asset-types")


def _asset_type_to_dict(at):
    return {
        "id": at.id,
        "name": at.name,
        "description": at.description,
        "template": at.template,
    }


@asset_types_bp.route("", methods=["POST"])
@require_admin
def create_asset_type():
    """Create a new asset type with markdown template"""
    try:
        asset_data = LocationTypeCreate(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    existing = db.exec(
        select(LocationType).where(LocationType.name == asset_data.name)
    ).first()
    if existing:
        return jsonify({"detail": "Asset type with this name already exists"}), 409

    at = create_location_type(db, asset_data)
    return jsonify(_asset_type_to_dict(at)), 201


@asset_types_bp.route("/<int:asset_type_id>", methods=["GET"])
@require_auth
def get_asset_type(asset_type_id):
    """Get asset type by ID"""
    db = get_session()
    asset_type = get_location_type_by_id(db, asset_type_id)
    if not asset_type:
        return jsonify({"detail": "Asset type not found"}), 404
    return jsonify(_asset_type_to_dict(asset_type)), 200


@asset_types_bp.route("", methods=["GET"])
@require_auth
def list_asset_types():
    """List all asset types"""
    db = get_session()
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 100, type=int)
    asset_types = get_all_location_types(db, skip, limit)
    return jsonify([_asset_type_to_dict(at) for at in asset_types]), 200


@asset_types_bp.route("/initialize-defaults", methods=["POST"])
@require_admin
def initialize_defaults():
    """Initialize default asset types for scout organizations"""
    db = get_session()
    asset_types = initialize_default_asset_types(db)
    return jsonify([_asset_type_to_dict(at) for at in asset_types]), 201
