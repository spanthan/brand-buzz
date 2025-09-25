from pydantic import BaseModel
from typing import List, Optional
from app.schemas.product import ProductOut
from app.schemas.user import UserOut

class BrandBase(BaseModel):
    name: str

class BrandCreate(BrandBase):
    pass

class BrandOut(BrandBase):
    id: int
    products: List[ProductOut] = []
    users: List[UserOut] = []

    class Config:
        orm_mode = True
