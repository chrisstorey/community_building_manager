"""
Database abstraction layer - supports SQLite and PostgreSQL.
Uses SQLModel for unified ORM + schema definitions.
"""
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.engine import Engine

from app.config import settings


def get_database_url() -> str:
    """Get database URL from settings."""
    return settings.database_url


def create_db_engine() -> Engine:
    """Create database engine from settings."""
    url = get_database_url()

    # Additional kwargs for SQLite
    if "sqlite" in url:
        return create_engine(url, connect_args={"check_same_thread": False})

    # PostgreSQL or other databases
    return create_engine(url, pool_pre_ping=True)


# Create engine
engine = create_db_engine()


def get_session():
    """Dependency for getting database session."""
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize database - create all tables."""
    SQLModel.metadata.create_all(engine)
