"""User model"""
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
import enum


class UserRole(str, enum.Enum):
    """User roles in the system"""
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.VIEWER)
    is_active: bool = Field(default=True)
    organization_id: int = Field(foreign_key="organizations.id")
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="users")
    updates: list["Update"] = Relationship(back_populates="user")
