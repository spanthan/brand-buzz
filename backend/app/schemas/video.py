from pydantic import BaseModel

class VideoBase(BaseModel):
    platform: str
    url: str

class VideoCreate(VideoBase):
    product_id: int

class VideoOut(VideoBase):
    id: int
    product_id: int

    class Config:
        orm_mode = True
