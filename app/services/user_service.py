"""User management service"""
from sqlmodel import Session, select
from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate
from app.core.security import get_password_hash


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    db_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=user.role,
        organization_id=user.organization_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email"""
    return db.exec(select(User).where(User.email == email)).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Get user by ID"""
    return db.get(User, user_id)


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User | None:
    """Update user"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(update_data)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
