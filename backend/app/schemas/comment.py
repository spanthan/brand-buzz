from pydantic import BaseModel
from typing import List

class CommentBase(BaseModel):
    text: str
    sentiment: str | None = None

class CommentCreate(CommentBase):
    video_id: int

class CommentOut(CommentBase):
    id: int
    video_id: int
    keywords: List[str] = []   # show just keyword text

    class Config:
        orm_mode = True
