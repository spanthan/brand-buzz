from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.db.base_class import Base

class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="brand")
    users: Mapped[list["User"]] = relationship("User", back_populates="brand")
