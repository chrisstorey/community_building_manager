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
from app.services.work_service import generate_work_items_from_template

# Predefined asset types with maintenance templates
DEFAULT_ASSET_TYPES = {
    "Scout HQ": """## Area: Roof and Gutters
- Inspect for leaks and damage
- Clear gutters and downspouts
- Check flashing around chimney

## Area: Exterior Walls
- Inspect for cracks and water damage
- Check siding condition
- Inspect doors and frames

## Area: HVAC System
- Replace air filters monthly
- Service heating system annually
- Check thermostat calibration
- Clean AC condensers

## Area: Electrical System
- Test emergency lighting
- Inspect outlet safety
- Check panel for corrosion
- Test emergency power systems

## Area: Plumbing
- Check for leaks under sinks
- Inspect toilet operation
- Test water pressure
- Drain water heater sediment

## Area: Interior
- Check all light fixtures
- Inspect flooring condition
- Check doors and locks
- Inspect ceiling and walls

## Area: Safety Systems
- Test fire alarm system
- Inspect fire extinguishers
- Check emergency exits
- Test First Aid kits""",

    "Church": """## Area: Roof and Structure
- Inspect roof for leaks
- Check structural supports
- Inspect steeple/bell tower
- Check gutters and downspouts

## Area: Windows and Doors
- Inspect stained glass windows
- Check door frames and hinges
- Inspect seals for drafts
- Test locks

## Area: Interior Maintenance
- Sweep and mop floors
- Dust pews and furniture
- Clean altar area
- Maintain organ/music instruments

## Area: HVAC System
- Replace air filters
- Service heating system
- Test temperature control
- Clean vents

## Area: Electrical
- Test emergency lighting
- Check outlet functionality
- Inspect light fixtures
- Test backup power

## Area: Plumbing
- Check toilets and sinks
- Inspect baptismal font plumbing
- Check water pressure
- Inspect pipes for leaks

## Area: Grounds
- Mow grass and trim hedges
- Maintain landscaping
- Inspect walkways
- Repair any damage""",

    "Church Hall": """## Area: Roof and Exterior
- Inspect roof condition
- Check gutters and downspouts
- Inspect siding/cladding
- Check doors and frames

## Area: Interior Flooring
- Clean and maintain flooring
- Inspect for damage
- Repair cracks
- Polish as needed

## Area: HVAC System
- Replace air filters
- Service heating/cooling
- Check temperature control
- Clean vents and ducts

## Area: Electrical System
- Test all lighting
- Check outlets safety
- Inspect circuit panel
- Test emergency systems

## Area: Plumbing
- Check kitchen sink and taps
- Inspect toilets
- Test water pressure
- Look for leaks

## Area: Windows and Doors
- Clean windows inside/outside
- Inspect frames
- Test locks
- Check seals

## Area: Kitchen Facilities
- Clean appliances
- Check refrigerator seals
- Inspect stove
- Check water heater""",

    "Scout Activity Centre": """## Area: Activity Spaces
- Inspect flooring condition
- Check wall condition
- Inspect lighting fixtures
- Check ventilation

## Area: Sports Equipment
- Inspect sports equipment safety
- Check mats and padding
- Inspect climbing wall
- Check activity stations

## Area: Kitchen Facilities
- Clean and sanitize surfaces
- Check appliances
- Inspect food storage
- Check plumbing

## Area: Bathrooms and Showers
- Clean and disinfect
- Check plumbing
- Inspect fixtures
- Check soap/towel dispensers

## Area: Sleeping Areas
- Check bedding condition
- Inspect mattresses
- Check windows
- Inspect furniture

## Area: Outdoor Areas
- Inspect playground equipment
- Check surface condition
- Trim vegetation
- Repair any damage

## Area: Safety and Security
- Inspect fire safety equipment
- Check emergency exits
- Test emergency lighting
- Verify first aid kits
- Check security locks""",

    "Scout Campsite": """## Area: Site Grounds
- Inspect camping pitches for hazards
- Check ground drainage
- Clear overhanging branches
- Inspect boundary fencing

## Area: Toilet and Shower Facilities
- Clean and disinfect all facilities
- Check plumbing for leaks
- Inspect hot water system
- Check ventilation and lighting

## Area: Cooking Facilities
- Inspect camp kitchen equipment
- Check gas connections and appliances
- Clean grease traps and drainage
- Inspect fire suppression equipment

## Area: Water Supply
- Test water quality
- Inspect storage tanks
- Check pumping equipment
- Inspect distribution pipework

## Area: Electrical Supply
- Test all power hookup points
- Inspect distribution board
- Test residual current devices
- Check outdoor lighting

## Area: Structures and Buildings
- Inspect huts and shelters for damage
- Check roof condition on all buildings
- Inspect doors and windows
- Check foundations for subsidence

## Area: Safety and Emergency
- Inspect fire pits and BBQ areas
- Check first aid provisions
- Inspect emergency access routes
- Test emergency communication equipment
- Check fire extinguishers""",

    "Community Building": """## Area: Roof and Exterior
- Inspect roof for leaks and damage
- Check gutters and downspouts
- Inspect external cladding
- Check signage and accessibility

## Area: Main Hall
- Inspect flooring condition
- Check ceiling and walls
- Test all lighting
- Inspect acoustic panels

## Area: Meeting Rooms
- Check flooring and furnishings
- Inspect windows and blinds
- Test heating and ventilation
- Check AV equipment

## Area: Kitchen and Catering
- Clean and sanitize all surfaces
- Check appliances and equipment
- Inspect plumbing
- Check refrigeration temperatures

## Area: Toilets and Accessible Facilities
- Clean and disinfect
- Check all plumbing fixtures
- Inspect accessible toilet facilities
- Replenish consumables

## Area: HVAC System
- Replace air filters
- Service boiler/heat pump
- Check temperature controls
- Inspect ventilation ducts

## Area: Electrical Systems
- Test emergency lighting
- Inspect distribution board
- Check all outlets and switches
- Test fire alarm and emergency systems

## Area: Accessibility and Safety
- Inspect ramps and handrails
- Check hearing loop system
- Test fire alarm and extinguishers
- Inspect emergency exits and signage
- Check CCTV and security systems"""
}


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
    """Get all locations for an organization (excluding soft-deleted)"""
    return list(
        db.exec(
            select(Location)
            .where(Location.organization_id == org_id)
            .where(Location.is_deleted == False)
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
    db_location.updated_at = _now_utc()

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

    # Generate work items from template
    asset_type = get_location_type_by_id(db, asset_type_id)
    if asset_type and asset_type.template:
        generate_work_items_from_template(db, db_asset, asset_type.template)

    return db_asset


def delete_location(db: Session, location_id: int) -> bool:
    """Soft delete a location"""
    db_location = get_location_by_id(db, location_id)
    if not db_location:
        return False

    db_location.is_deleted = True
    db_location.updated_at = _now_utc()
    db.add(db_location)
    db.commit()
    return True


def search_locations(
    db: Session,
    org_id: int | None = None,
    query: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Location]:
    """Search locations by name, address, or other criteria"""
    statement = select(Location).where(Location.is_deleted == False)

    if org_id:
        statement = statement.where(Location.organization_id == org_id)

    if query:
        search_term = f"%{query}%"
        statement = statement.where(
            (Location.name.ilike(search_term)) | (Location.address.ilike(search_term))
        )

    if status:
        statement = statement.where(Location.status == status)

    statement = statement.offset(skip).limit(limit)
    return list(db.exec(statement).all())


def initialize_default_asset_types(db: Session) -> list[LocationType]:
    """Initialize or fetch default asset types"""
    created_types = []

    for asset_name, template in DEFAULT_ASSET_TYPES.items():
        # Check if asset type already exists
        existing = db.exec(
            select(LocationType).where(LocationType.name == asset_name)
        ).first()

        if not existing:
            asset_type = LocationType(
                name=asset_name,
                description=f"Scout organization {asset_name.lower()} with standard maintenance template",
                template=template
            )
            db.add(asset_type)
            created_types.append(asset_type)

    if created_types:
        db.commit()
        for asset_type in created_types:
            db.refresh(asset_type)

    # Return all asset types (newly created + existing ones)
    return db.exec(select(LocationType)).all()


def get_location_assets(
    db: Session, location_id: int
) -> list[LocationAsset]:
    """Get all assets for a location"""
    return list(
        db.exec(
            select(LocationAsset)
            .where(LocationAsset.location_id == location_id)
        ).all()
    )


def remove_asset_from_location(
    db: Session, location_id: int, asset_id: int
) -> bool:
    """Remove an asset from a location"""
    db_asset = db.get(LocationAsset, asset_id)
    if not db_asset or db_asset.location_id != location_id:
        return False

    db.delete(db_asset)
    db.commit()
    return True
