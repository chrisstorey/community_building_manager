"""Work area and work item models"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class WorkArea(Base):
    """Work area - represents a category of maintenance items for an asset"""
    __tablename__ = "work_areas"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("location_assets.id"), nullable=False)
    statement = Column(Text, nullable=False)
    is_relevant = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("LocationAsset", back_populates="work_areas")
    items = relationship("WorkItem", back_populates="work_area")


class WorkItem(Base):
    """Work item - represents a specific maintenance task"""
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True)
    work_area_id = Column(Integer, ForeignKey("work_areas.id"), nullable=False)
    statement = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    work_area = relationship("WorkArea", back_populates="items")
    updates = relationship("Update", back_populates="work_item")


class Update(Base):
    """Update - represents a progress update on a work item"""
    __tablename__ = "updates"

    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    narrative = Column(Text, nullable=False)
    review_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    work_item = relationship("WorkItem", back_populates="updates")
    user = relationship("User", back_populates="updates")
