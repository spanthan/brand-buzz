from pydantic import BaseModel

class KeywordBase(BaseModel):
    text: str

class KeywordCreate(KeywordBase):
    pass

class KeywordOut(KeywordBase):
    id: int

    class Config:
        orm_mode = True
