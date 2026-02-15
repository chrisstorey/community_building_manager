"""Organization and Location management routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db import get_session
from app.models.user import User
from app.core.dependencies import get_manager_user, get_current_user
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    LocationCreate,
    LocationResponse,
    LocationUpdate,
    LocationTypeCreate,
    LocationTypeResponse,
)
from app.services.organization_service import (
    create_organization,
    get_organization_by_id,
    update_organization,
    create_location,
    get_location_by_id,
    get_locations_for_organization,
    update_location,
    create_location_type,
    get_location_type_by_id,
    get_all_location_types,
    add_asset_to_location,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_org(
    org: OrganizationCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Create a new organization"""
    return create_organization(db, org)


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_org(
    org_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get organization by ID"""
    org = get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return org


@router.patch("/{org_id}", response_model=OrganizationResponse)
def update_org(
    org_id: int,
    org_update: OrganizationUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Update organization"""
    org = update_organization(db, org_id, org_update)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return org


@router.post("/{org_id}/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_loc(
    org_id: int,
    location: LocationCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Create a location for an organization"""
    org = get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    location.organization_id = org_id
    return create_location(db, location)


@router.get("/{org_id}/locations", response_model=list[LocationResponse])
def list_locations(
    org_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List locations for an organization"""
    org = get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    return get_locations_for_organization(db, org_id, skip, limit)


@router.get("/locations/{location_id}", response_model=LocationResponse)
def get_loc(
    location_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get location by ID"""
    location = get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return location


@router.patch("/locations/{location_id}", response_model=LocationResponse)
def update_loc(
    location_id: int,
    location_update: LocationUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Update location"""
    location = update_location(db, location_id, location_update)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return location


@router.post(
    "/locations/{location_id}/assets/{asset_type_id}",
    status_code=status.HTTP_201_CREATED,
)
def add_asset(
    location_id: int,
    asset_type_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Add an asset type instance to a location"""
    location = get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )

    asset_type = get_location_type_by_id(db, asset_type_id)
    if not asset_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset type not found"
        )

    return add_asset_to_location(db, location_id, asset_type_id)
