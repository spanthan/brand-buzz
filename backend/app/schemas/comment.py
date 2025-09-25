from pydantic import BaseModel
from typing import List
from app.schemas.comment_keyword import CommentKeywordOut

class CommentBase(BaseModel):
    text: str
    sentiment: str | None = None

class CommentCreate(CommentBase):
    video_id: int
    keywords: List[int] = []  # keyword IDs to attach

class CommentOut(CommentBase):
    id: int
    video_id: int
    keywords: List[CommentKeywordOut] = []  # join objects with weight

    class Config:
        orm_mode = True
