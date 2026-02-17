"""Organization and Location management routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.db import get_session
from app.models.user import User
from app.models.organization import LocationAsset
from app.core.dependencies import get_manager_user, get_current_user
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    LocationCreate,
    LocationCreateRequest,
    LocationResponse,
    LocationUpdate,
    LocationAssetResponse,
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
    location_request: LocationCreateRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Create a location for an organization"""
    org = get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    location = LocationCreate(
        **location_request.model_dump(),
        organization_id=org_id
    )
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


@router.get("/locations/search", response_model=list[LocationResponse])
def search_loc(
    q: str | None = Query(None, description="Search query"),
    org_id: int | None = Query(None, description="Filter by organization"),
    status_filter: str | None = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Search locations by name, address, or filter by organization and status"""
    return search_locations(
        db, org_id=org_id, query=q, status=status_filter, skip=skip, limit=limit
    )


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


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loc(
    location_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Delete (soft delete) a location"""
    location = get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )

    delete_location(db, location_id)
    return None


@router.post(
    "/locations/{location_id}/assets/{asset_type_id}",
    response_model=LocationAssetResponse,
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


@router.get("/locations/{location_id}/assets", response_model=list[LocationAssetResponse])
def get_assets(
    location_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all assets for a location"""
    location = get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )

    assets = get_location_assets(db, location_id)
    return assets


@router.delete(
    "/locations/{location_id}/assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_asset(
    location_id: int,
    asset_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_manager_user),
):
    """Remove an asset from a location"""
    location = get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )

    success = remove_asset_from_location(db, location_id, asset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )

    return None
