"""
Database abstraction layer - supports SQLite and PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine

from app.config import settings

# Create base class for all models
Base = declarative_base()


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


# Create engine and session factory
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Dependency for getting database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    """Initialize database - create all tables."""
    Base.metadata.create_all(bind=engine)
