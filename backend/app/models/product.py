from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"))
    name = Column(String, index=True, nullable=False)

    brand = relationship("Brand", back_populates="products")
    videos = relationship("Video", back_populates="product", cascade="all, delete-orphan")