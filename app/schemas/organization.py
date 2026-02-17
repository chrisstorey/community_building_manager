"""Organization and Location schemas"""
from pydantic import BaseModel
from datetime import datetime


class KeyContactCreate(BaseModel):
    """Key contact creation schema"""
    name: str
    title: str | None = None
    email: str | None = None
    phone: str | None = None


class KeyContactResponse(KeyContactCreate):
    """Key contact response schema"""
    model_config = {"from_attributes": True}

    id: int


class LocationAssetResponse(BaseModel):
    """Location asset response schema"""
    model_config = {"from_attributes": True}

    id: int
    location_id: int
    asset_type_id: int
    created_at: datetime
    updated_at: datetime


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str
    address: str | None = None
    parent_organization_id: int | None = None


class OrganizationCreate(OrganizationBase):
    """Organization creation schema"""
    pass


class OrganizationUpdate(BaseModel):
    """Organization update schema"""
    name: str | None = None
    address: str | None = None


class OrganizationResponse(OrganizationBase):
    """Organization response schema"""
    model_config = {"from_attributes": True}

    id: int
    created_at: datetime
    updated_at: datetime
    key_contacts: list[KeyContactResponse] = []


class LocationBase(BaseModel):
    """Base location schema"""
    name: str
    address: str
    latitude: float | None = None
    longitude: float | None = None
    status: str = "active"
    opening_hours: str | None = None
    capacity: int | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None


class LocationCreate(LocationBase):
    """Location creation schema"""
    organization_id: int


class LocationCreateRequest(LocationBase):
    """Location creation request schema"""
    pass


class LocationUpdate(BaseModel):
    """Location update schema"""
    name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str | None = None
    opening_hours: str | None = None
    capacity: int | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None


class LocationResponse(LocationBase):
    """Location response schema"""
    model_config = {"from_attributes": True}

    id: int
    organization_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class LocationTypeBase(BaseModel):
    """Base location type schema"""
    name: str
    description: str | None = None
    template: str


class LocationTypeCreate(LocationTypeBase):
    """Location type creation schema"""
    pass


class LocationTypeResponse(LocationTypeBase):
    """Location type response schema"""
    model_config = {"from_attributes": True}

    id: int
