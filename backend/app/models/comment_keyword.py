from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, ForeignKey
from app.db.base_class import Base

class CommentKeyword(Base):
    __tablename__ = "comment_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id"))

    comment: Mapped["Comment"] = relationship("Comment", back_populates="keywords")
    keyword: Mapped["Keyword"] = relationship("Keyword", back_populates="comment_keywords")

