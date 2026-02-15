"""Work area and work item schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UpdateCreate(BaseModel):
    """Update creation schema"""
    narrative: str
    review_date: Optional[datetime] = None


class UpdateResponse(UpdateCreate):
    """Update response schema"""
    id: int
    work_item_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkItemBase(BaseModel):
    """Base work item schema"""
    statement: str
    description: Optional[str] = None


class WorkItemCreate(WorkItemBase):
    """Work item creation schema"""
    work_area_id: int


class WorkItemResponse(WorkItemBase):
    """Work item response schema"""
    id: int
    work_area_id: int
    created_at: datetime
    updated_at: datetime
    updates: List[UpdateResponse] = []

    class Config:
        from_attributes = True


class WorkAreaBase(BaseModel):
    """Base work area schema"""
    statement: str
    is_relevant: bool = True


class WorkAreaCreate(WorkAreaBase):
    """Work area creation schema"""
    asset_id: int


class WorkAreaResponse(WorkAreaBase):
    """Work area response schema"""
    id: int
    asset_id: int
    created_at: datetime
    updated_at: datetime
    items: List[WorkItemResponse] = []

    class Config:
        from_attributes = True
