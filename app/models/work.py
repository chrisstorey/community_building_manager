"""Work area and work item models"""
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class WorkArea(SQLModel, table=True):
    """Work area - represents a category of maintenance items for an asset"""
    __tablename__ = "work_areas"

    id: int | None = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="location_assets.id")
    statement: str
    is_relevant: bool = Field(default=True)
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    # Relationships
    asset: Optional["LocationAsset"] = Relationship(back_populates="work_areas")
    items: list["WorkItem"] = Relationship(back_populates="work_area")


class WorkItem(SQLModel, table=True):
    """Work item - represents a specific maintenance task"""
    __tablename__ = "work_items"

    id: int | None = Field(default=None, primary_key=True)
    work_area_id: int = Field(foreign_key="work_areas.id")
    statement: str = Field(max_length=255)
    description: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    # Relationships
    work_area: Optional[WorkArea] = Relationship(back_populates="items")
    updates: list["Update"] = Relationship(back_populates="work_item")


class Update(SQLModel, table=True):
    """Update - represents a progress update on a work item"""
    __tablename__ = "updates"

    id: int | None = Field(default=None, primary_key=True)
    work_item_id: int = Field(foreign_key="work_items.id")
    user_id: int = Field(foreign_key="users.id")
    narrative: str
    review_date: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=_now_utc)

    # Relationships
    work_item: Optional[WorkItem] = Relationship(back_populates="updates")
    user: Optional["User"] = Relationship(back_populates="updates")
