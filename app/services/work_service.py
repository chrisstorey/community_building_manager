"""Work area and work item service"""
from sqlalchemy.orm import Session
from app.models.work import WorkArea, WorkItem, Update
from app.models.organization import LocationAsset, LocationType
from app.schemas.work import WorkAreaCreate, WorkItemCreate, UpdateCreate
from datetime import datetime


def parse_markdown_template(template: str) -> list[tuple[str, list[str]]]:
    """
    Parse markdown template into work areas and items.
    Expected format:
    ## Area Title
    - Item 1
    - Item 2

    ## Another Area
    - Item 3
    """
    areas = []
    current_area = None
    current_items = []

    for line in template.split("\n"):
        line = line.strip()

        # Check for area headers (h2 or h3)
        if line.startswith("## ") or line.startswith("### "):
            if current_area:
                areas.append((current_area, current_items))
            current_area = line.lstrip("# ").strip()
            current_items = []
        # Check for list items
        elif line.startswith("- ") or line.startswith("* "):
            item_text = line.lstrip("-* ").strip()
            if item_text:
                current_items.append(item_text)

    # Don't forget the last area
    if current_area:
        areas.append((current_area, current_items))

    return areas


def generate_work_items_from_template(
    db: Session, asset: LocationAsset, template: str
) -> list[WorkArea]:
    """Generate work areas and items from markdown template"""
    areas_data = parse_markdown_template(template)
    created_areas = []

    for area_statement, items in areas_data:
        # Create work area
        work_area = WorkArea(
            asset_id=asset.id,
            statement=area_statement,
            is_relevant=True,
        )
        db.add(work_area)
        db.flush()  # Get the ID without committing

        # Create work items
        for item_statement in items:
            work_item = WorkItem(
                work_area_id=work_area.id,
                statement=item_statement,
                description=None,
            )
            db.add(work_item)

        created_areas.append(work_area)

    db.commit()
    return created_areas


def get_work_areas_for_asset(db: Session, asset_id: int) -> list[WorkArea]:
    """Get all work areas for an asset"""
    return db.query(WorkArea).filter(WorkArea.asset_id == asset_id).all()


def get_work_area_by_id(db: Session, area_id: int) -> WorkArea | None:
    """Get work area by ID"""
    return db.query(WorkArea).filter(WorkArea.id == area_id).first()


def update_work_area_relevance(
    db: Session, area_id: int, is_relevant: bool
) -> WorkArea | None:
    """Update work area relevance status"""
    area = get_work_area_by_id(db, area_id)
    if not area:
        return None

    area.is_relevant = is_relevant
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


def get_work_items_for_area(db: Session, area_id: int) -> list[WorkItem]:
    """Get all work items for a work area"""
    return db.query(WorkItem).filter(WorkItem.work_area_id == area_id).all()


def get_work_item_by_id(db: Session, item_id: int) -> WorkItem | None:
    """Get work item by ID"""
    return db.query(WorkItem).filter(WorkItem.id == item_id).first()


def add_update_to_item(
    db: Session, item_id: int, user_id: int, narrative: str, review_date: datetime | None = None
) -> Update | None:
    """Add an update to a work item"""
    item = get_work_item_by_id(db, item_id)
    if not item:
        return None

    update = Update(
        work_item_id=item_id,
        user_id=user_id,
        narrative=narrative,
        review_date=review_date,
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


def get_updates_for_item(db: Session, item_id: int) -> list[Update]:
    """Get all updates for a work item"""
    return db.query(Update).filter(Update.work_item_id == item_id).all()


def get_outstanding_items(db: Session, org_id: int) -> list[WorkItem]:
    """Get outstanding work items (items without recent updates) for an organization"""
    # This is a simplified version - items without updates in the last review period
    from sqlalchemy import and_, or_

    # Get items where there are no updates or the last update review date has passed
    outstanding = (
        db.query(WorkItem)
        .join(WorkArea)
        .join(LocationAsset)
        .join("location")
        .filter(LocationAsset.location.organization_id == org_id)
        .filter(
            or_(
                ~WorkItem.updates.any(),
                WorkItem.updates.any(Update.review_date < datetime.utcnow()),
            )
        )
        .all()
    )
    return outstanding
