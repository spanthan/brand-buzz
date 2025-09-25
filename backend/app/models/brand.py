from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
    users = relationship("User", back_populates="brand", cascade="all, delete-orphan")