"""Organization and Location models"""
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Organization(SQLModel, table=True):
    """Organization model - represents a community organization"""
    __tablename__ = "organizations"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    address: str | None = Field(default=None)
    parent_organization_id: int | None = Field(
        default=None, foreign_key="organizations.id"
    )
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    # Relationships
    users: list["User"] = Relationship(back_populates="organization")
    locations: list["Location"] = Relationship(back_populates="organization")
    key_contacts: list["KeyContact"] = Relationship(back_populates="organization")
    child_organizations: list["Organization"] = Relationship(
        back_populates="parent_organization",
        sa_relationship_kwargs={"remote_side": "Organization.id"},
    )
    parent_organization: Optional["Organization"] = Relationship(
        back_populates="child_organizations",
        sa_relationship_kwargs={"remote_side": "Organization.parent_organization_id"},
    )


class KeyContact(SQLModel, table=True):
    """Key contact for an organization"""
    __tablename__ = "key_contacts"

    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id")
    name: str = Field(max_length=255)
    title: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=_now_utc)

    # Relationships
    organization: Optional[Organization] = Relationship(back_populates="key_contacts")


class LocationType(SQLModel, table=True):
    """Asset types that can be assigned to locations"""
    __tablename__ = "location_types"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, unique=True)
    description: str | None = Field(default=None)
    template: str  # Markdown template

    # Relationships
    location_assets: list["LocationAsset"] = Relationship(back_populates="asset_type")


class Location(SQLModel, table=True):
    """Location model - represents a physical location within an organization"""
    __tablename__ = "locations"

    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id")
    name: str = Field(max_length=255)
    address: str
    latitude: float | None = Field(default=None, description="GPS latitude coordinate")
    longitude: float | None = Field(default=None, description="GPS longitude coordinate")
    status: str = Field(
        default="active",
        description="Location status: active, inactive, under_maintenance"
    )
    opening_hours: str | None = Field(
        default=None,
        description="Operating hours in format 'Mon-Fri 09:00-17:00; Sat 10:00-14:00'"
    )
    capacity: int | None = Field(default=None, description="Location capacity/max occupants")
    contact_person: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: str | None = Field(default=None, max_length=255)
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    # Relationships
    organization: Optional[Organization] = Relationship(back_populates="locations")
    assets: list["LocationAsset"] = Relationship(back_populates="location")


class LocationAsset(SQLModel, table=True):
    """An asset instance assigned to a location"""
    __tablename__ = "location_assets"

    id: int | None = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="locations.id")
    asset_type_id: int = Field(foreign_key="location_types.id")
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    # Relationships
    location: Optional[Location] = Relationship(back_populates="assets")
    asset_type: Optional[LocationType] = Relationship(back_populates="location_assets")
    work_areas: list["WorkArea"] = Relationship(back_populates="asset")
