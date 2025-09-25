from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.db.base_class import Base

class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String, unique=True, index=True)

    comment_keywords: Mapped[list["CommentKeyword"]] = relationship("CommentKeyword", back_populates="keyword")
