from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey
from app.db.base_class import Base

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str | None] = mapped_column(String, nullable=True)

    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))
    video: Mapped["Video"] = relationship("Video", back_populates="comments")

    keywords: Mapped[list["CommentKeyword"]] = relationship("CommentKeyword", back_populates="comment")
