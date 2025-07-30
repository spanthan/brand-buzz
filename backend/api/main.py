import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.db_loader import *


# FastAPI setup
app = FastAPI(debug=True)

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/comments")
def get_comments():
    db = SessionLocal()
    records = db.query(CommentKeywordMap).all()

    cleaned_comments = [
        {
            "text": record.text,
            "keywords": record.keywords
        }
        for record in records
        if record.text and record.keywords
    ]

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
