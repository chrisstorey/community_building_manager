"""Asset type management routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.db import get_session
from app.models.user import User
from app.models.organization import LocationType
from app.core.dependencies import get_admin_user, get_current_user
from app.schemas.organization import LocationTypeCreate, LocationTypeResponse
from app.services.organization_service import (
    create_location_type,
    get_location_type_by_id,
    get_all_location_types,
)

router = APIRouter(prefix="/asset-types", tags=["asset-types"])


@router.post("", response_model=LocationTypeResponse, status_code=status.HTTP_201_CREATED)
def create_asset_type(
    asset_type: LocationTypeCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    """Create a new asset type with markdown template"""
    # Check for unique name
    existing = db.exec(
        select(LocationType).where(LocationType.name == asset_type.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Asset type with this name already exists",
        )

    return create_location_type(db, asset_type)


@router.get("/{asset_type_id}", response_model=LocationTypeResponse)
def get_asset_type(
    asset_type_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get asset type by ID"""
    asset_type = get_location_type_by_id(db, asset_type_id)
    if not asset_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset type not found"
        )
    return asset_type


@router.get("", response_model=list[LocationTypeResponse])
def list_asset_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all asset types"""
    return get_all_location_types(db, skip, limit)
