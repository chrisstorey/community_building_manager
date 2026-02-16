"""Pytest configuration and fixtures"""
import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_session
from fastapi.testclient import TestClient


# Test database setup - use in-memory SQLite with shared connection
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test and drop after."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def db_session():
    """Database session fixture for tests."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(db_session):
    """Test client fixture that shares the same db session."""
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
