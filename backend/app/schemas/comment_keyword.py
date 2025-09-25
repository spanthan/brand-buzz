from pydantic import BaseModel

class CommentKeywordBase(BaseModel):
    weight: float = 1.0

class CommentKeywordCreate(CommentKeywordBase):
    comment_id: int
    keyword_id: int

class CommentKeywordOut(CommentKeywordBase):
    id: int
    comment_id: int
    keyword_id: int

    class Config:
        orm_mode = True
