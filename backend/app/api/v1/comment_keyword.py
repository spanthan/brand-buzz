from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.comment_keyword import CommentKeywordCreate, CommentKeywordOut
from app.crud import comment_keyword as crud_ck
from app.api.deps import get_db

router = APIRouter(prefix="/comment-keywords", tags=["comment_keywords"])

@router.post("/", response_model=CommentKeywordOut)
def create_comment_keyword(mapping: CommentKeywordCreate, db: Session = Depends(get_db)):
    return crud_ck.create_comment_keyword(db, mapping)

@router.get("/comment/{comment_id}", response_model=List[CommentKeywordOut])
def get_keywords_for_comment(comment_id: int, db: Session = Depends(get_db)):
    return crud_ck.get_keywords_for_comment(db, comment_id)

@router.get("/keyword/{keyword_id}", response_model=List[CommentKeywordOut])
def get_comments_for_keyword(keyword_id: int, db: Session = Depends(get_db)):
    return crud_ck.get_comments_for_keyword(db, keyword_id)

@router.put("/{mapping_id}", response_model=CommentKeywordOut)
def update_mapping_weight(mapping_id: int, weight: float, db: Session = Depends(get_db)):
    updated = crud_ck.update_comment_keyword_weight(db, mapping_id, weight)
    if not updated:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return updated

@router.delete("/{mapping_id}", response_model=CommentKeywordOut)
def delete_mapping(mapping_id: int, db: Session = Depends(get_db)):
    deleted = crud_ck.delete_comment_keyword(db, mapping_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return deleted
