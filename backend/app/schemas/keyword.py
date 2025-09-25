from pydantic import BaseModel
from typing import List
from app.schemas.comment_keyword import CommentKeywordOut

class KeywordBase(BaseModel):
    text: str

class KeywordCreate(KeywordBase):
    pass

class KeywordOut(KeywordBase):
    id: int
    comment_keywords: List[CommentKeywordOut] = []

    class Config:
        orm_mode = True
