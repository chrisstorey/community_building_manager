"""Dashboard API endpoints"""
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify
from sqlalchemy import and_, or_
from sqlmodel import Session, select

from app.db import get_session
from app.models.work import WorkItem, Update, WorkArea
from app.models.organization import LocationAsset, Location
from app.core.dependencies import get_current_user, require_auth

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def _get_outstanding_items_for_org(db: Session, org_id: int) -> list[WorkItem]:
    """Get outstanding work items for an organization"""
    now = datetime.now(timezone.utc)

    outstanding = list(
        db.exec(
            select(WorkItem)
            .join(WorkArea)
            .join(LocationAsset)
            .join(Location, LocationAsset.location_id == Location.id)
            .where(Location.organization_id == org_id)
            .where(
                or_(
                    ~WorkItem.updates.any(),
                    WorkItem.updates.any(and_(
                        Update.review_date.isnot(None),
                        Update.review_date < now
                    ))
                )
            )
        ).all()
    )
    return outstanding


def _get_items_due_next_month(db: Session, org_id: int) -> list[WorkItem]:
    """Get work items due in the next 30 days"""
    now = datetime.now(timezone.utc)
    next_month = now + timedelta(days=30)

    due_items = list(
        db.exec(
            select(WorkItem)
            .join(WorkArea)
            .join(LocationAsset)
            .join(Location, LocationAsset.location_id == Location.id)
            .where(Location.organization_id == org_id)
            .where(
                WorkItem.updates.any(and_(
                    Update.review_date.isnot(None),
                    Update.review_date >= now,
                    Update.review_date <= next_month
                ))
            )
        ).all()
    )
    return due_items


def _count_total_items_for_org(db: Session, org_id: int) -> int:
    """Count total work items for an organization"""
    items = db.exec(
        select(WorkItem)
        .join(WorkArea)
        .join(LocationAsset)
        .join(Location, LocationAsset.location_id == Location.id)
        .where(Location.organization_id == org_id)
    ).all()
    return len(items)


def _item_to_dict(item, location):
    """Convert item to dictionary"""
    last_update = item.updates[-1] if item.updates else None
    days_since = None
    now = datetime.now(timezone.utc)
    if last_update:
        created = last_update.created_at
        if created.tzinfo is None:
            days_since = (now.replace(tzinfo=None) - created).days
        else:
            days_since = (now - created).days

    return {
        "id": item.id,
        "statement": item.statement,
        "work_area_statement": item.work_area.statement,
        "location_name": location.name if location else "Unknown",
        "days_since_update": days_since,
    }


@dashboard_bp.route("/stats/<int:org_id>", methods=["GET"])
@require_auth
def get_dashboard_stats(org_id):
    """Get dashboard statistics for an organization"""
    current_user = get_current_user()
    if current_user.organization_id != org_id:
        return jsonify({"detail": "Access denied to this organization"}), 403

    db = get_session()
    outstanding = len(_get_outstanding_items_for_org(db, org_id))
    due_next_month = len(_get_items_due_next_month(db, org_id))
    total = _count_total_items_for_org(db, org_id)

    return jsonify({
        "outstanding_count": outstanding,
        "due_next_month_count": due_next_month,
        "total_items": total,
    }), 200


@dashboard_bp.route("/outstanding/<int:org_id>", methods=["GET"])
@require_auth
def get_outstanding_items(org_id):
    """Get outstanding work items for an organization"""
    current_user = get_current_user()
    if current_user.organization_id != org_id:
        return jsonify({"detail": "Access denied to this organization"}), 403

    db = get_session()
    items = _get_outstanding_items_for_org(db, org_id)

    result = []
    for item in items:
        location = db.exec(
            select(Location)
            .join(LocationAsset, Location.id == LocationAsset.location_id)
            .join(WorkArea, LocationAsset.id == WorkArea.asset_id)
            .where(WorkArea.id == item.work_area_id)
        ).first()
        result.append(_item_to_dict(item, location))

    return jsonify(result), 200


@dashboard_bp.route("/due-soon/<int:org_id>", methods=["GET"])
@require_auth
def get_due_soon_items(org_id):
    """Get work items due soon for an organization"""
    current_user = get_current_user()
    if current_user.organization_id != org_id:
        return jsonify({"detail": "Access denied to this organization"}), 403

    db = get_session()
    items = _get_items_due_next_month(db, org_id)

    result = []
    for item in items:
        location = db.exec(
            select(Location)
            .join(LocationAsset, Location.id == LocationAsset.location_id)
            .join(WorkArea, LocationAsset.id == WorkArea.asset_id)
            .where(WorkArea.id == item.work_area_id)
        ).first()
        result.append(_item_to_dict(item, location))

    return jsonify(result), 200
