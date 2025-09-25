from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.comment import CommentCreate, CommentOut
from app.crud import comment as crud_comment
from app.api.deps import get_db

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentOut)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    return crud_comment.create_comment(db, comment, keywords=comment.keywords)

@router.get("/video/{video_id}", response_model=List[CommentOut])
def get_comments_by_video(video_id: int, db: Session = Depends(get_db)):
    return crud_comment.get_comments_by_video(db, video_id)
