"""Work items and work areas routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.db import get_session
from app.models.user import User
from app.core.dependencies import get_current_user, get_manager_user
from app.schemas.work import (
    WorkAreaResponse,
    WorkItemResponse,
    UpdateCreate,
    UpdateResponse,
)
from app.services.work_service import (
    get_work_areas_for_asset,
    get_work_area_by_id,
    update_work_area_relevance,
    get_work_items_for_area,
    get_work_item_by_id,
    add_update_to_item,
    get_updates_for_item,
    get_outstanding_items,
)

router = APIRouter(prefix="/work", tags=["work-items"])


@router.get("/assets/{asset_id}/areas", response_model=list[WorkAreaResponse])
def list_work_areas(
    asset_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all work areas for an asset"""
    areas = get_work_areas_for_asset(db, asset_id)
    return areas


@router.get("/areas/{area_id}", response_model=WorkAreaResponse)
def get_work_area(
    area_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a specific work area"""
    area = get_work_area_by_id(db, area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work area not found"
        )
    return area


@router.patch("/areas/{area_id}/relevance", response_model=WorkAreaResponse)
def set_area_relevance(
    area_id: int,
    is_relevant: bool,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Update work area relevance status"""
    area = update_work_area_relevance(db, area_id, is_relevant)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work area not found"
        )
    return area


@router.get("/areas/{area_id}/items", response_model=list[WorkItemResponse])
def list_work_items(
    area_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all work items for a work area"""
    area = get_work_area_by_id(db, area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work area not found"
        )
    items = get_work_items_for_area(db, area_id)
    return items


@router.get("/items/{item_id}", response_model=WorkItemResponse)
def get_work_item(
    item_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a specific work item"""
    item = get_work_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work item not found"
        )
    return item


@router.post("/items/{item_id}/updates", response_model=UpdateResponse, status_code=status.HTTP_201_CREATED)
def add_item_update(
    item_id: int,
    update_data: UpdateCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Add an update to a work item"""
    item = get_work_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work item not found"
        )

    update = add_update_to_item(
        db,
        item_id,
        current_user.id,
        update_data.narrative,
        update_data.review_date,
    )
    return update


@router.get("/items/{item_id}/updates", response_model=list[UpdateResponse])
def list_item_updates(
    item_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all updates for a work item"""
    item = get_work_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work item not found"
        )

    updates = get_updates_for_item(db, item_id)
    return updates


@router.get("/outstanding", response_model=list[WorkItemResponse])
def list_outstanding_items(
    organization_id: int = Query(..., description="Organization ID"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get outstanding work items for an organization"""
    items = get_outstanding_items(db, organization_id)
    return items
