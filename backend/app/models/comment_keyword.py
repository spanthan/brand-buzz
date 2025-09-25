from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base import Base

class CommentKeyword(Base):
    __tablename__ = "comment_keywords"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"))
    weight = Column(Float, default=1.0)

    comment = relationship("Comment", back_populates="keywords")
    keyword = relationship("Keyword", back_populates="comment_keywords")
