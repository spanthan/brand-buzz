from pydantic import BaseModel
from typing import List
from app.schemas.video import VideoOut

class ProductBase(BaseModel):
    name: str

class ProductCreate(ProductBase):
    brand_id: int

class ProductOut(ProductBase):
    id: int
    brand_id: int
    videos: List[VideoOut] = []

    class Config:
        orm_mode = True
