"""Organization management service"""
from sqlmodel import Session, select
from app.models.organization import Organization, Location, LocationType, LocationAsset
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    LocationCreate,
    LocationUpdate,
    LocationTypeCreate,
)


def create_organization(db: Session, org: OrganizationCreate) -> Organization:
    """Create a new organization"""
    db_org = Organization(**org.model_dump())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org


def get_organization_by_id(db: Session, org_id: int) -> Organization | None:
    """Get organization by ID"""
    return db.get(Organization, org_id)


def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> list[Organization]:
    """Get all organizations with pagination"""
    return list(db.exec(select(Organization).offset(skip).limit(limit)).all())


def update_organization(
    db: Session, org_id: int, org_update: OrganizationUpdate
) -> Organization | None:
    """Update organization"""
    db_org = get_organization_by_id(db, org_id)
    if not db_org:
        return None

    update_data = org_update.model_dump(exclude_unset=True)
    db_org.sqlmodel_update(update_data)

    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org


def create_location(db: Session, location: LocationCreate) -> Location:
    """Create a new location"""
    db_location = Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_location_by_id(db: Session, location_id: int) -> Location | None:
    """Get location by ID"""
    return db.get(Location, location_id)


def get_locations_for_organization(
    db: Session, org_id: int, skip: int = 0, limit: int = 100
) -> list[Location]:
    """Get all locations for an organization"""
    return list(
        db.exec(
            select(Location)
            .where(Location.organization_id == org_id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


def update_location(
    db: Session, location_id: int, location_update: LocationUpdate
) -> Location | None:
    """Update location"""
    db_location = get_location_by_id(db, location_id)
    if not db_location:
        return None

    update_data = location_update.model_dump(exclude_unset=True)
    db_location.sqlmodel_update(update_data)

    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def create_location_type(db: Session, loc_type: LocationTypeCreate) -> LocationType:
    """Create a new location type with template"""
    db_type = LocationType(**loc_type.model_dump())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type


def get_location_type_by_id(db: Session, type_id: int) -> LocationType | None:
    """Get location type by ID"""
    return db.get(LocationType, type_id)


def get_all_location_types(
    db: Session, skip: int = 0, limit: int = 100
) -> list[LocationType]:
    """Get all location types"""
    return list(db.exec(select(LocationType).offset(skip).limit(limit)).all())


def add_asset_to_location(
    db: Session, location_id: int, asset_type_id: int
) -> LocationAsset:
    """Add an asset type instance to a location"""
    db_asset = LocationAsset(location_id=location_id, asset_type_id=asset_type_id)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset
