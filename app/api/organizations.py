"""Organization and Location management routes"""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.db import get_session
from app.core.dependencies import require_manager, require_auth, get_current_user
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    LocationCreate,
    LocationCreateRequest,
    LocationUpdate,
)
from app.services.organization_service import (
    create_organization,
    get_organization_by_id,
    update_organization,
    create_location,
    get_location_by_id,
    get_locations_for_organization,
    update_location,
    delete_location,
    search_locations,
    get_location_type_by_id,
    add_asset_to_location,
    get_location_assets,
    remove_asset_from_location,
)

org_bp = Blueprint("organizations", __name__, url_prefix="/organizations")


def _org_to_dict(org):
    return {
        "id": org.id,
        "name": org.name,
        "address": org.address,
    }


def _location_to_dict(loc):
    return {
        "id": loc.id,
        "name": loc.name,
        "address": loc.address,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "status": loc.status,
        "organization_id": loc.organization_id,
    }


def _asset_to_dict(asset):
    return {
        "id": asset.id,
        "location_id": asset.location_id,
        "asset_type_id": asset.asset_type_id,
    }


@org_bp.route("", methods=["POST"])
@require_manager
def create_org():
    """Create a new organization"""
    try:
        org_data = OrganizationCreate(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    org = create_organization(db, org_data)
    return jsonify(_org_to_dict(org)), 201


@org_bp.route("/<int:org_id>", methods=["GET"])
@require_auth
def get_org(org_id):
    """Get organization by ID"""
    db = get_session()
    org = get_organization_by_id(db, org_id)
    if not org:
        return jsonify({"detail": "Organization not found"}), 404
    return jsonify(_org_to_dict(org)), 200


@org_bp.route("/<int:org_id>", methods=["PATCH"])
@require_manager
def update_org(org_id):
    """Update organization"""
    try:
        org_update = OrganizationUpdate(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    org = update_organization(db, org_id, org_update)
    if not org:
        return jsonify({"detail": "Organization not found"}), 404
    return jsonify(_org_to_dict(org)), 200


@org_bp.route("/<int:org_id>/locations", methods=["POST"])
@require_manager
def create_loc(org_id):
    """Create a location for an organization"""
    db = get_session()
    org = get_organization_by_id(db, org_id)
    if not org:
        return jsonify({"detail": "Organization not found"}), 404

    try:
        loc_req = LocationCreateRequest(**request.get_json())
        location = LocationCreate(**loc_req.model_dump(), organization_id=org_id)
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    loc = create_location(db, location)
    return jsonify(_location_to_dict(loc)), 201


@org_bp.route("/<int:org_id>/locations", methods=["GET"])
@require_auth
def list_locations(org_id):
    """List locations for an organization"""
    db = get_session()
    org = get_organization_by_id(db, org_id)
    if not org:
        return jsonify({"detail": "Organization not found"}), 404

    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 100, type=int)
    locations = get_locations_for_organization(db, org_id, skip, limit)
    return jsonify([_location_to_dict(loc) for loc in locations]), 200


@org_bp.route("/locations/search", methods=["GET"])
@require_auth
def search_loc():
    """Search locations"""
    db = get_session()
    q = request.args.get("q")
    org_id = request.args.get("org_id", type=int)
    status_filter = request.args.get("status_filter")
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 100, type=int)

    locations = search_locations(db, org_id=org_id, query=q, status=status_filter, skip=skip, limit=limit)
    return jsonify([_location_to_dict(loc) for loc in locations]), 200


@org_bp.route("/locations/<int:location_id>", methods=["GET"])
@require_auth
def get_loc(location_id):
    """Get location by ID"""
    db = get_session()
    location = get_location_by_id(db, location_id)
    if not location:
        return jsonify({"detail": "Location not found"}), 404
    return jsonify(_location_to_dict(location)), 200


@org_bp.route("/locations/<int:location_id>", methods=["PATCH"])
@require_manager
def update_loc(location_id):
    """Update location"""
    try:
        loc_update = LocationUpdate(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    location = update_location(db, location_id, loc_update)
    if not location:
        return jsonify({"detail": "Location not found"}), 404
    return jsonify(_location_to_dict(location)), 200


@org_bp.route("/locations/<int:location_id>", methods=["DELETE"])
@require_manager
def delete_loc(location_id):
    """Delete (soft delete) a location"""
    db = get_session()
    location = get_location_by_id(db, location_id)
    if not location:
        return jsonify({"detail": "Location not found"}), 404
    delete_location(db, location_id)
    return "", 204


@org_bp.route("/locations/<int:location_id>/assets/<int:asset_type_id>", methods=["POST"])
@require_manager
def add_asset(location_id, asset_type_id):
    """Add an asset type instance to a location"""
    db = get_session()
    location = get_location_by_id(db, location_id)
    if not location:
        return jsonify({"detail": "Location not found"}), 404

    asset_type = get_location_type_by_id(db, asset_type_id)
    if not asset_type:
        return jsonify({"detail": "Asset type not found"}), 404

    asset = add_asset_to_location(db, location_id, asset_type_id)
    return jsonify(_asset_to_dict(asset)), 201


@org_bp.route("/locations/<int:location_id>/assets", methods=["GET"])
@require_auth
def get_assets(location_id):
    """Get all assets for a location"""
    db = get_session()
    location = get_location_by_id(db, location_id)
    if not location:
        return jsonify({"detail": "Location not found"}), 404

    assets = get_location_assets(db, location_id)
    return jsonify([_asset_to_dict(asset) for asset in assets]), 200


@org_bp.route("/locations/<int:location_id>/assets/<int:asset_id>", methods=["DELETE"])
@require_manager
def remove_asset(location_id, asset_id):
    """Remove an asset from a location"""
    db = get_session()
    location = get_location_by_id(db, location_id)
    if not location:
        return jsonify({"detail": "Location not found"}), 404

    success = remove_asset_from_location(db, location_id, asset_id)
    if not success:
        return jsonify({"detail": "Asset not found"}), 404

    return "", 204
