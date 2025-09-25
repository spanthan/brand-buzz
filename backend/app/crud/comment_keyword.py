from sqlalchemy.orm import Session
from app.models.comment_keyword import CommentKeyword
from app.schemas.comment_keyword import CommentKeywordCreate

def create_comment_keyword(db: Session, mapping: CommentKeywordCreate) -> CommentKeyword:
    db_mapping = CommentKeyword(
        comment_id=mapping.comment_id,
        keyword_id=mapping.keyword_id,
        weight=mapping.weight
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

def get_keywords_for_comment(db: Session, comment_id: int):
    return db.query(CommentKeyword).filter(CommentKeyword.comment_id == comment_id).all()

def get_comments_for_keyword(db: Session, keyword_id: int):
    return db.query(CommentKeyword).filter(CommentKeyword.keyword_id == keyword_id).all()

def update_comment_keyword_weight(db: Session, mapping_id: int, weight: float):
    mapping = db.query(CommentKeyword).filter(CommentKeyword.id == mapping_id).first()
    if not mapping:
        return None
    mapping.weight = weight
    db.commit()
    db.refresh(mapping)
    return mapping

def delete_comment_keyword(db: Session, mapping_id: int):
    mapping = db.query(CommentKeyword).filter(CommentKeyword.id == mapping_id).first()
    if not mapping:
        return None
    db.delete(mapping)
    db.commit()
    return mapping
