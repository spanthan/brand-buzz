import json
import os
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database URL from environment variable
# DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://shalini_suade:shalini@localhost:5432/suade_db")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://shalini:Xjv0FWlbmwdJiZA6l1jMusy8fgis5i6w@dpg-d255naqli9vc73ev3bn0-a.virginia-postgres.render.com/suade_db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define DB models
class ThemeNode(Base):
    __tablename__ = "nodes"

    keyword = Column(String, primary_key=True, index=True)
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


class CommentKeywordMap(Base):
    __tablename__ = "comment_keyword_map"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    sentiment = Column(String, nullable=True)
    keywords = Column(JSON)  # stores list of keywords

# Create tables if not exist
Base.metadata.create_all(bind=engine)

def load_comments_to_db(json_path="comment_keyword_map.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # list of {text, sentiment, keywords}

    db = SessionLocal()

    # Optional: Clear old data
    db.query(CommentKeywordMap).delete()
    db.commit()

    for item in data:
        comment = CommentKeywordMap(
            text=item["text"],
            sentiment=item.get("sentiment", None),
            keywords=item.get("keywords", [])
        )
        db.add(comment)

    db.commit()
    db.close()
    print(f"✅ Loaded {len(data)} comments into the database")

def load_graph_data_to_db(json_path="theme_graph.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()

    # Optional: Clear old data
    db.query(ThemeLink).delete()
    db.query(ThemeNode).delete()
    db.commit()

    for node in data["nodes"]:
        db_node = ThemeNode(keyword=node["keyword"], weight=node["weight"], sentiment=node["sentiment"])
        db.add(db_node)

    for link in data["links"]:
        db_link = ThemeLink(source=link["source"], target=link["target"], value=link["value"])
        db.add(db_link)

    db.commit()
    db.close()
    print("✅ Database updated with graph data")
