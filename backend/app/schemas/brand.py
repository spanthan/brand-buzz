from pydantic import BaseModel
from typing import List

class BrandBase(BaseModel):
    name: str

class BrandCreate(BrandBase):
    pass

class BrandOut(BrandBase):
    id: int

    class Config:
        orm_mode = True
