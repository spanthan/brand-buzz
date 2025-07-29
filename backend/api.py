import json
from theme_and_graph import *

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# FastAPI setup
app = FastAPI(debug=True)

origins = [
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAlchemy setup
DATABASE_URL = "postgresql://shalini_suade:shalini@localhost:5432/suade_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define the tables
class ThemeNode(Base):
    __tablename__ = "nodes"

    keyword = Column(String, primary_key=True, index=True)
    weight = Column(Integer)
    sentiment = Column(String)

class ThemeLink(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String)
    target = Column(String)
    value = Column(Float)

# Initialize DB
Base.metadata.create_all(bind=engine)

def load_graph_data_to_db(json_path="theme_graph.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()

    # Optional: Clear old data
    db.query(ThemeNode).delete()
    db.query(ThemeLink).delete()
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

@app.get("/graph")
def get_graph_data():
    # have this here if running for a specific tiktok
    # comments, keywords = extract_keywords_llm()
    # run_embedding_pipeline(keywords)
    # build_graph()
    # load_graph_data_to_db()
    db = SessionLocal()
    nodes = db.query(ThemeNode).all()
    links = db.query(ThemeLink).all()

    node_dicts = [{"keyword": n.keyword, "weight": n.weight, "sentiment": n.sentiment} for n in nodes]
    link_dicts = [{"source": l.source, "target": l.target, "value": l.value} for l in links]

    # print(node_dicts)
    # print(link_dicts)

    return {"nodes": node_dicts, "links": link_dicts}

# @app.get("/graph")
# def get_graph_data():
#     with open("theme_graph.json", "r") as f:
#         data = json.load(f)
#     return data

# Optional: Load DB on server start
@app.on_event("startup")
def startup_event():
    print("⏳ Loading JSON into database...")
    comments, keywords = extract_keywords_llm()
    run_embedding_pipeline(keywords)
    build_graph()
    load_graph_data_to_db()
    print("✅ FastAPI backend is ready.")
