"""Dashboard API endpoints"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_
from sqlmodel import Session, select

from app.db import get_session
from app.models.user import User
from app.models.work import WorkItem, Update, WorkArea
from app.models.organization import LocationAsset, Location
from app.core.dependencies import get_current_user
from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    outstanding_count: int
    due_next_month_count: int
    total_items: int


class OutstandingItem(BaseModel):
    """Outstanding work item"""
    id: int
    statement: str
    work_area_statement: str
    location_name: str
    days_since_update: int | None


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _get_outstanding_items_for_org(db: Session, org_id: int) -> list[WorkItem]:
    """Get outstanding work items for an organization"""
    now = datetime.now(timezone.utc)

    # Items without any updates OR with last update review date in the past
    outstanding = list(
        db.exec(
            select(WorkItem)
            .join(WorkArea)
            .join(LocationAsset)
            .join(Location, LocationAsset.location_id == Location.id)
            .where(Location.organization_id == org_id)
            .where(
                or_(
                    ~WorkItem.updates.any(),  # No updates at all
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

    # Items with updates due in next 30 days
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


@router.get("/stats/{org_id}", response_model=DashboardStats)
def get_dashboard_stats(
    org_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics for an organization"""
    # Verify user has access to this organization
    if current_user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )

    outstanding = len(_get_outstanding_items_for_org(db, org_id))
    due_next_month = len(_get_items_due_next_month(db, org_id))
    total = _count_total_items_for_org(db, org_id)

    return DashboardStats(
        outstanding_count=outstanding,
        due_next_month_count=due_next_month,
        total_items=total,
    )


@router.get("/outstanding/{org_id}", response_model=list[OutstandingItem])
def get_outstanding_items(
    org_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get outstanding work items for an organization"""
    # Verify user has access to this organization
    if current_user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )

    items = _get_outstanding_items_for_org(db, org_id)
    now = datetime.now(timezone.utc)

    result = []
    for item in items:
        # Find the location name
        location = db.exec(
            select(Location)
            .join(LocationAsset, Location.id == LocationAsset.location_id)
            .join(WorkArea, LocationAsset.id == WorkArea.asset_id)
            .where(WorkArea.id == item.work_area_id)
        ).first()

        # Calculate days since last update
        last_update = item.updates[-1] if item.updates else None
        days_since = None
        if last_update:
            created = last_update.created_at
            if created.tzinfo is None:
                days_since = (now.replace(tzinfo=None) - created).days
            else:
                days_since = (now - created).days

        result.append(OutstandingItem(
            id=item.id,
            statement=item.statement,
            work_area_statement=item.work_area.statement,
            location_name=location.name if location else "Unknown",
            days_since_update=days_since,
        ))

    return result


@router.get("/due-soon/{org_id}", response_model=list[OutstandingItem])
def get_due_soon_items(
    org_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get work items due soon for an organization"""
    # Verify user has access to this organization
    if current_user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )

    items = _get_items_due_next_month(db, org_id)
    now = datetime.now(timezone.utc)

    result = []
    for item in items:
        # Find the location name
        location = db.exec(
            select(Location)
            .join(LocationAsset, Location.id == LocationAsset.location_id)
            .join(WorkArea, LocationAsset.id == WorkArea.asset_id)
            .where(WorkArea.id == item.work_area_id)
        ).first()

        # Calculate days since last update
        last_update = item.updates[-1] if item.updates else None
        days_since = None
        if last_update:
            created = last_update.created_at
            if created.tzinfo is None:
                days_since = (now.replace(tzinfo=None) - created).days
            else:
                days_since = (now - created).days

        result.append(OutstandingItem(
            id=item.id,
            statement=item.statement,
            work_area_statement=item.work_area.statement,
            location_name=location.name if location else "Unknown",
            days_since_update=days_since,
        ))

    return result
