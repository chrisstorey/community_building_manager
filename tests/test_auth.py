"""Tests for authentication"""
import pytest
from sqlmodel import Session

from app.models.user import User, UserRole
from app.models.organization import Organization
from app.schemas.auth import UserCreate
from app.services.user_service import get_user_by_email, create_user
from app.core.security import verify_password, get_password_hash


def test_user_creation(db_session: Session):
    """Test user creation"""
    # Create organization first
    org = Organization(name="Test Org", address="123 Main St")
    db_session.add(org)
    db_session.commit()

    # Create user
    user_create = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
        role=UserRole.MANAGER,
        organization_id=org.id,
    )
    user = create_user(db_session, user_create)

    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role == UserRole.MANAGER
    assert user.is_active is True
    assert verify_password("testpassword123", user.hashed_password)


def test_get_user_by_email(db_session: Session):
    """Test getting user by email"""
    org = Organization(name="Test Org", address="123 Main St")
    db_session.add(org)
    db_session.commit()

    user_create = UserCreate(
        email="test@example.com",
        password="testpassword123",
        organization_id=org.id,
    )
    created_user = create_user(db_session, user_create)

    # Get user by email
    found_user = get_user_by_email(db_session, "test@example.com")
    assert found_user is not None
    assert found_user.email == "test@example.com"
    assert found_user.id == created_user.id


def test_login_endpoint(client, db_session: Session):
    """Test login endpoint"""
    # Create organization and user
    org = Organization(name="Test Org", address="123 Main St")
    db_session.add(org)
    db_session.commit()

    user_create = UserCreate(
        email="test@example.com",
        password="testpassword123",
        organization_id=org.id,
    )
    create_user(db_session, user_create)

    # Test login
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_register_endpoint(client, db_session: Session):
    """Test register endpoint"""
    # Create organization first
    org = Organization(name="Test Org", address="123 Main St")
    db_session.add(org)
    db_session.commit()

    # Register user
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "testpassword123",
            "full_name": "New User",
            "organization_id": org.id,
        },
    )
    assert response.status_code == 201
    assert response.json["email"] == "newuser@example.com"


def test_register_duplicate_email(client, db_session: Session):
    """Test register with duplicate email"""
    org = Organization(name="Test Org", address="123 Main St")
    db_session.add(org)
    db_session.commit()

    user_create = UserCreate(
        email="test@example.com",
        password="testpassword123",
        organization_id=org.id,
    )
    create_user(db_session, user_create)

    # Try to register with same email
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "organization_id": org.id,
        },
    )
    assert response.status_code == 409
