from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    role: str = "member"

class UserCreate(UserBase):
    password: str
    brand_id: int

class UserOut(UserBase):
    id: int
    brand_id: int

    class Config:
        orm_mode = True
