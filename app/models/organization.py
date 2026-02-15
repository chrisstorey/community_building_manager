"""Organization and Location models"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Organization(Base):
    """Organization model - represents a community organization"""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    parent_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    locations = relationship("Location", back_populates="organization")
    child_organizations = relationship(
        "Organization",
        remote_side=[id],
        backref="parent_organization"
    )
    key_contacts = relationship("KeyContact", back_populates="organization")


class KeyContact(Base):
    """Key contact for an organization"""
    __tablename__ = "key_contacts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="key_contacts")


class LocationType(Base):
    """Asset types that can be assigned to locations"""
    __tablename__ = "location_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)  # Markdown template

    # Relationships
    location_assets = relationship("LocationAsset", back_populates="asset_type")


class Location(Base):
    """Location model - represents a physical location within an organization"""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="locations")
    assets = relationship("LocationAsset", back_populates="location")


class LocationAsset(Base):
    """An asset instance assigned to a location"""
    __tablename__ = "location_assets"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    asset_type_id = Column(Integer, ForeignKey("location_types.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="assets")
    asset_type = relationship("LocationType", back_populates="location_assets")
    work_areas = relationship("WorkArea", back_populates="asset")
