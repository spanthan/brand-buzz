from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        brand_id=user.brand_id,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users_by_brand(db: Session, brand_id: int):
    return db.query(User).filter(User.brand_id == brand_id).all()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user
