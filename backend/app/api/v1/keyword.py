from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.keyword import KeywordCreate, KeywordOut
from app.crud import keyword as crud_keyword
from app.api.deps import get_db

router = APIRouter(prefix="/keywords", tags=["keywords"])

@router.post("/", response_model=KeywordOut)
def create_keyword(keyword: KeywordCreate, db: Session = Depends(get_db)):
    return crud_keyword.create_keyword(db, keyword)

@router.get("/", response_model=List[KeywordOut])
def get_keywords(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_keyword.get_all_keywords(db, skip=skip, limit=limit)
