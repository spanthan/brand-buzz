import json
from theme_and_graph import *

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from db_loader import *


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

@app.get("/comments")
def get_comments():
    with open("../comment_keyword_map.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_comments = []

    for item in data:
        if "text" in item and "keywords" in item:
            cleaned_comments.append({
                "text": item["text"],
                "keywords": item["keywords"]
            })

    return cleaned_comments

@app.get("/graph")
def get_graph_data():
    db = SessionLocal()
    nodes = db.query(ThemeNode).all()
    links = db.query(ThemeLink).all()

    node_dicts = [{"keyword": n.keyword, "weight": n.weight, "sentiment": n.sentiment} for n in nodes]
    
    link_dicts = [
        {
            "source": l.source_node.keyword,
            "target": l.target_node.keyword,
            "value": l.value
        }
        for l in links
    ]

    return {"nodes": node_dicts, "links": link_dicts}

# Optional: Load DB on server start
@app.on_event("startup")
def startup_event():
    print("⏳ Loading JSON into database...")
    load_graph_data_to_db()
    print("✅ FastAPI backend is ready.")
