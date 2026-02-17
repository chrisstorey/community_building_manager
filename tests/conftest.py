"""Pytest configuration and fixtures"""
import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app as flask_app
import app.db as db_module


# Test database setup - use in-memory SQLite
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test and drop after."""
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def db_session():
    """Database session fixture for tests."""
    session = Session(test_engine)
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Test client fixture for Flask app."""
    flask_app.config["TESTING"] = True

    # Override get_session to return test session
    def get_test_session():
        return db_session

    # Patch at module level
    original_get_session = db_module.get_session
    db_module.get_session = get_test_session

    with flask_app.test_client() as test_client:
        yield test_client

    # Restore original
    db_module.get_session = original_get_session
