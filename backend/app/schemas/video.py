from pydantic import BaseModel
from typing import List
from app.schemas.comment import CommentOut

class VideoBase(BaseModel):
    platform: str
    url: str

class VideoCreate(VideoBase):
    product_id: int

class VideoOut(VideoBase):
    id: int
    product_id: int
    comments: List[CommentOut] = []

    class Config:
        orm_mode = True
