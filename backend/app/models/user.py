from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="member")  # "admin" or "member"
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"))

    brand = relationship("Brand", back_populates="users")
