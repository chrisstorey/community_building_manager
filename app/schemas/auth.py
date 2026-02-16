"""Authentication schemas"""
from pydantic import BaseModel
from datetime import datetime

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: str
    full_name: str | None = None
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    organization_id: int


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: str | None = None
    role: UserRole | None = None


class UserResponse(UserBase):
    """User response schema"""
    model_config = {"from_attributes": True}

    id: int
    is_active: bool
    organization_id: int
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request schema"""
    email: str
    password: str
