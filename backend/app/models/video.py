from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    platform = Column(String, nullable=False)  # e.g., TikTok, YouTube
    url = Column(String, unique=True, nullable=False)

    product = relationship("Product", back_populates="videos")
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")