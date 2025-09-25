import json
import os
from sqlalchemy import func, case, create_engine, Column, String, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from collections import defaultdict, Counter
from itertools import combinations


# Database URL
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://shalini_suade:shalini@localhost:5432/suade_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -----------------------
# Core Entities
# -----------------------

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True)

    products = relationship("Product", back_populates="brand")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    name = Column(String, index=True)

    brand = relationship("Brand", back_populates="products")
    videos = relationship("Video", back_populates="product")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    platform = Column(String)  # e.g. TikTok, YouTube
    url = Column(String, unique=True)

    product = relationship("Product", back_populates="videos")
    comments = relationship("Comment", back_populates="video")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    text = Column(Text, nullable=False)
    sentiment = Column(String, nullable=True)

    video = relationship("Video", back_populates="comments")
    keywords = relationship("CommentKeyword", back_populates="comment")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, unique=True, index=True)

    comment_keywords = relationship("CommentKeyword", back_populates="keyword")


class CommentKeyword(Base):
    __tablename__ = "comment_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(Integer, ForeignKey("comments.id"))
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    weight = Column(Float, default=1.0)  # optional: for frequency/importance

    comment = relationship("Comment", back_populates="keywords")
    keyword = relationship("Keyword", back_populates="comment_keywords")

# -----------------------
# Graph Entities
# -----------------------

class ThemeNode(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String, ForeignKey("keywords.text"), index=True)
    weight = Column(Integer)
    sentiment = Column(String)

    outgoing_links = relationship("ThemeLink", back_populates="source_node", foreign_keys="ThemeLink.source")
    incoming_links = relationship("ThemeLink", back_populates="target_node", foreign_keys="ThemeLink.target")


class ThemeLink(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, ForeignKey("nodes.keyword"))
    target = Column(String, ForeignKey("nodes.keyword"))
    value = Column(Float)

    source_node = relationship("ThemeNode", foreign_keys=[source], back_populates="outgoing_links")
    target_node = relationship("ThemeNode", foreign_keys=[target], back_populates="incoming_links")


# -----------------------
# Create Tables
# -----------------------
Base.metadata.create_all(bind=engine)

def load_comments_to_db(json_path="comment_keyword_map.json", 
                        brand_name="DefaultBrand", 
                        product_name="DefaultProduct", 
                        video_url="http://example.com", 
                        platform="YouTube"):
    """
    Load comments and keywords into the normalized schema:
    Brand -> Product -> Video -> Comment -> CommentKeyword -> Keyword
    """

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # list of {text, sentiment, keywords}

    db = SessionLocal()

    # Ensure brand exists
    brand = db.query(Brand).filter_by(name=brand_name).first()
    if not brand:
        brand = Brand(name=brand_name)
        db.add(brand)
        db.commit()
        db.refresh(brand)

    # Ensure product exists
    product = db.query(Product).filter_by(name=product_name, brand_id=brand.id).first()
    if not product:
        product = Product(name=product_name, brand=brand)
        db.add(product)
        db.commit()
        db.refresh(product)

    # Ensure video exists
    video = db.query(Video).filter_by(url=video_url).first()
    if not video:
        video = Video(product=product, url=video_url, platform=platform)
        db.add(video)
        db.commit()
        db.refresh(video)

    # Optional: Clear old comments for this video
    db.query(Comment).filter_by(video_id=video.id).delete()
    db.commit()

    # Insert comments and keywords
    for item in data:
        comment = Comment(
            video=video,
            text=item["text"],
            sentiment=item.get("sentiment", None),
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        for kw_text in item.get("keywords", []):
            # ensure keyword exists
            keyword = db.query(Keyword).filter_by(text=kw_text).first()
            if not keyword:
                keyword = Keyword(text=kw_text)
                db.add(keyword)
                db.commit()
                db.refresh(keyword)

            # create comment-keyword mapping
            ck = CommentKeyword(comment=comment, keyword=keyword, weight=1.0)
            db.add(ck)

        db.commit()

    db.close()
    print(f"✅ Loaded {len(data)} comments into DB under video {video_url}")

def build_graph_from_db(brand_id: int = None):
    db = SessionLocal()

    query = (
        db.query(
            Keyword.text,
            func.count(CommentKeyword.id).label("weight"),
            func.sum(case((Comment.sentiment == "positive", 1), else_=0)).label("pos"),
            func.sum(case((Comment.sentiment == "negative", 1), else_=0)).label("neg"),
            func.sum(case((Comment.sentiment == "neutral", 1), else_=0)).label("neu"),
        )
        .join(CommentKeyword, CommentKeyword.keyword_id == Keyword.id)
        .join(Comment, Comment.id == CommentKeyword.comment_id)
        .join(Video, Video.id == Comment.video_id)
        .join(Product, Product.id == Video.product_id)
        .join(Brand, Brand.id == Product.brand_id)
    )

    if brand_id:
        query = query.filter(Brand.id == brand_id)

    keyword_stats = query.group_by(Keyword.text).all()

    nodes = []
    for text, weight, pos, neg, neu in keyword_stats:
        sentiment_counts = {"positive": pos, "negative": neg, "neutral": neu}
        dominant = max(sentiment_counts.items(), key=lambda x: x[1])[0]
        nodes.append({
            "keyword": text.lower(),
            "weight": int(weight),
            "sentiment": dominant
        })

    # Links: co-occurrence of keywords per comment
    rows = (
        db.query(Comment.id, Keyword.text)
        .join(CommentKeyword, CommentKeyword.comment_id == Comment.id)
        .join(Keyword, Keyword.id == CommentKeyword.keyword_id)
        .join(Video, Video.id == Comment.video_id)
        .join(Product, Product.id == Video.product_id)
        .join(Brand, Brand.id == Product.brand_id)
    )
    if brand_id:
        rows = rows.filter(Brand.id == brand_id)

    rows = rows.all()

    comment_to_keywords = defaultdict(list)
    for cid, ktext in rows:
        comment_to_keywords[cid].append(ktext.lower())

    co_occurrence = Counter()
    for kws in comment_to_keywords.values():
        for kw1, kw2 in combinations(sorted(set(kws)), 2):
            co_occurrence[(kw1, kw2)] += 1

    links = [
        {"source": kw1, "target": kw2, "value": val}
        for (kw1, kw2), val in co_occurrence.items()
    ]

    db.close()
    return {"nodes": nodes, "links": links}
