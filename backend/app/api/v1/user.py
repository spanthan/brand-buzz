from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserOut
from app.crud import user as crud_user
from app.api.deps import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user)

@router.get("/brand/{brand_id}", response_model=List[UserOut])
def get_users_by_brand(brand_id: int, db: Session = Depends(get_db)):
    return crud_user.get_users_by_brand(db, brand_id)
