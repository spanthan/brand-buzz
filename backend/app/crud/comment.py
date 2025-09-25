from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.keyword import Keyword
from app.models.comment_keyword import CommentKeyword
from app.schemas.comment import CommentCreate

def create_comment(db: Session, comment: CommentCreate, keywords: list[str] = None) -> Comment:
    db_comment = Comment(video_id=comment.video_id, text=comment.text, sentiment=comment.sentiment)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    if keywords:
        for kw_text in keywords:
            keyword = db.query(Keyword).filter(Keyword.text == kw_text).first()
            if not keyword:
                keyword = Keyword(text=kw_text)
                db.add(keyword)
                db.commit()
                db.refresh(keyword)

            mapping = CommentKeyword(comment_id=db_comment.id, keyword_id=keyword.id, weight=1.0)
            db.add(mapping)

        db.commit()

    return db_comment

def get_comments_by_video(db: Session, video_id: int):
    return db.query(Comment).filter(Comment.video_id == video_id).all()

def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()

def delete_comment(db: Session, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    db.delete(comment)
    db.commit()
    return comment
