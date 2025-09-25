from pydantic import BaseModel
from typing import List

class ProductBase(BaseModel):
    name: str

class ProductCreate(ProductBase):
    brand_id: int

class ProductOut(ProductBase):
    id: int
    brand_id: int

    class Config:
        orm_mode = True
