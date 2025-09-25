from pydantic import BaseModel

# Base shared properties
class KeywordBase(BaseModel):
    text: str

# Used when creating a new keyword
class KeywordCreate(KeywordBase):
    pass

# Used when returning a keyword from the API
class KeywordOut(KeywordBase):
    id: int

    class Config:
        orm_mode = True
