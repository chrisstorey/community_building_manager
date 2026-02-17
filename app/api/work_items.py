"""Work items and work areas routes"""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.db import get_session
from app.core.dependencies import get_current_user, require_auth, require_manager
from app.schemas.work import (
    UpdateCreate,
    WorkAreaCreate,
    WorkItemCreate,
)
from app.services.work_service import (
    get_work_areas_for_asset,
    get_work_area_by_id,
    update_work_area_relevance,
    get_work_items_for_area,
    get_work_item_by_id,
    add_update_to_item,
    get_updates_for_item,
    create_work_area,
    create_work_item,
)

work_items_bp = Blueprint("work_items", __name__, url_prefix="/work")


def _area_to_dict(area):
    return {
        "id": area.id,
        "statement": area.statement,
        "is_relevant": area.is_relevant,
        "asset_id": area.asset_id,
    }


def _item_to_dict(item):
    return {
        "id": item.id,
        "statement": item.statement,
        "description": item.description,
        "work_area_id": item.work_area_id,
    }


def _update_to_dict(update):
    return {
        "id": update.id,
        "narrative": update.narrative,
        "user_id": update.user_id,
        "review_date": update.review_date.isoformat() if update.review_date else None,
        "created_at": update.created_at.isoformat() if update.created_at else None,
    }


@work_items_bp.route("/assets/<int:asset_id>/areas", methods=["POST"])
@require_manager
def add_work_area(asset_id):
    """Add a work area to an asset"""
    try:
        area_data = WorkAreaCreate(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    area_data.asset_id = asset_id
    area = create_work_area(db, area_data)
    return jsonify(_area_to_dict(area)), 201


@work_items_bp.route("/assets/<int:asset_id>/areas", methods=["GET"])
@require_auth
def list_work_areas(asset_id):
    """Get all work areas for an asset"""
    db = get_session()
    areas = get_work_areas_for_asset(db, asset_id)
    return jsonify([_area_to_dict(area) for area in areas]), 200


@work_items_bp.route("/areas/<int:area_id>", methods=["GET"])
@require_auth
def get_work_area(area_id):
    """Get a specific work area"""
    db = get_session()
    area = get_work_area_by_id(db, area_id)
    if not area:
        return jsonify({"detail": "Work area not found"}), 404
    return jsonify(_area_to_dict(area)), 200


@work_items_bp.route("/areas/<int:area_id>/relevance", methods=["PATCH"])
@require_manager
def set_area_relevance(area_id):
    """Update work area relevance status"""
    try:
        data = request.get_json()
        is_relevant = data.get("is_relevant", False)
    except (TypeError, ValueError):
        return jsonify({"detail": "Invalid request"}), 400

    db = get_session()
    area = update_work_area_relevance(db, area_id, is_relevant)
    if not area:
        return jsonify({"detail": "Work area not found"}), 404
    return jsonify(_area_to_dict(area)), 200


@work_items_bp.route("/areas/<int:area_id>/items", methods=["POST"])
@require_manager
def add_work_item(area_id):
    """Add a work item to a work area"""
    try:
        item_data = WorkItemCreate(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    item_data.work_area_id = area_id
    item = create_work_item(db, item_data)
    return jsonify(_item_to_dict(item)), 201


@work_items_bp.route("/areas/<int:area_id>/items", methods=["GET"])
@require_auth
def list_work_items(area_id):
    """Get all work items for a work area"""
    db = get_session()
    area = get_work_area_by_id(db, area_id)
    if not area:
        return jsonify({"detail": "Work area not found"}), 404
    items = get_work_items_for_area(db, area_id)
    return jsonify([_item_to_dict(item) for item in items]), 200


@work_items_bp.route("/items/<int:item_id>", methods=["GET"])
@require_auth
def get_work_item(item_id):
    """Get a specific work item"""
    db = get_session()
    item = get_work_item_by_id(db, item_id)
    if not item:
        return jsonify({"detail": "Work item not found"}), 404
    return jsonify(_item_to_dict(item)), 200


@work_items_bp.route("/items/<int:item_id>/updates", methods=["POST"])
@require_manager
def add_item_update(item_id):
    """Add an update to a work item"""
    try:
        update_data = UpdateCreate(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"detail": str(e)}), 400

    db = get_session()
    item = get_work_item_by_id(db, item_id)
    if not item:
        return jsonify({"detail": "Work item not found"}), 404

    current_user = get_current_user()
    update = add_update_to_item(
        db,
        item_id,
        current_user.id,
        update_data.narrative,
        update_data.review_date,
    )
    return jsonify(_update_to_dict(update)), 201


@work_items_bp.route("/items/<int:item_id>/updates", methods=["GET"])
@require_auth
def list_item_updates(item_id):
    """Get all updates for a work item"""
    db = get_session()
    item = get_work_item_by_id(db, item_id)
    if not item:
        return jsonify({"detail": "Work item not found"}), 404

    updates = get_updates_for_item(db, item_id)
    return jsonify([_update_to_dict(u) for u in updates]), 200
