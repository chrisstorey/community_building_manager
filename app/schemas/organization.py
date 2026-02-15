"""Organization and Location schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class KeyContactCreate(BaseModel):
    """Key contact creation schema"""
    name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class KeyContactResponse(KeyContactCreate):
    """Key contact response schema"""
    id: int

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str
    address: Optional[str] = None
    parent_organization_id: Optional[int] = None


class OrganizationCreate(OrganizationBase):
    """Organization creation schema"""
    pass


class OrganizationUpdate(BaseModel):
    """Organization update schema"""
    name: Optional[str] = None
    address: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    """Organization response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    key_contacts: List[KeyContactResponse] = []

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    """Base location schema"""
    name: str
    address: str


class LocationCreate(LocationBase):
    """Location creation schema"""
    organization_id: int


class LocationUpdate(BaseModel):
    """Location update schema"""
    name: Optional[str] = None
    address: Optional[str] = None


class LocationResponse(LocationBase):
    """Location response schema"""
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocationTypeBase(BaseModel):
    """Base location type schema"""
    name: str
    description: Optional[str] = None
    template: str


class LocationTypeCreate(LocationTypeBase):
    """Location type creation schema"""
    pass


class LocationTypeResponse(LocationTypeBase):
    """Location type response schema"""
    id: int

    class Config:
        from_attributes = True
