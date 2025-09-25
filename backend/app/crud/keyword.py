from sqlalchemy.orm import Session
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate

def create_keyword(db: Session, keyword: KeywordCreate) -> Keyword:
    db_keyword = Keyword(text=keyword.text)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword

def get_keyword_by_text(db: Session, text: str):
    return db.query(Keyword).filter(Keyword.text == text).first()

def get_all_keywords(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Keyword).offset(skip).limit(limit).all()

def delete_keyword(db: Session, keyword_id: int):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        return None
    db.delete(keyword)
    db.commit()
    return keyword
