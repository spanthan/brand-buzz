import pandas as pd
import ollama
import re
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from sentiment_analysis import *
from db_loader import (
    load_comments_to_db, 
    load_graph_data_to_db
)
from db_graph_utils import (  # 👈 your new file with DB graph builders
    build_graph_from_db,
    add_llm_links,
    save_graph_to_json
)

# ------------------------
# CONFIG
# ------------------------

EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
SIMILARITY_THRESHOLD = 0.5
BORDERLINE_THRESHOLD = 0.4


# ------------------------
# LLM UTILITIES
# ------------------------

def run_llm(prompt, model="llama3"):
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content'].strip()


def extract_keywords_llm_helper(comments):
    print("🔍 Extracting keywords with LLM...")
    with open("prompts/keyword_prompt.txt", "r", encoding="utf-8") as file:
        template = file.read()

    prompt = template.format(comment_list=comments, length=20)
    response = run_llm(prompt)
    keywords = re.findall(r'"(.*?)"', response)
    return keywords


def extract_keywords_llm():
    print("📥 Loading final_comments.csv")

    df = pd.read_csv("final_comments.csv")
    comments = (
        df.dropna(subset=["text", "sentiment"])
        .apply(lambda row: f"{row['text']} [{row['sentiment']}]", axis=1)
        .tolist()
    )
    print(f"✅ Loaded {len(comments)} comments")

    keywords = extract_keywords_llm_helper(comments)

    while len(keywords) < 15:
        keywords = extract_keywords_llm_helper(comments)

    print("🧹 Deduplicating semantically similar phrases...")
    deduped_keywords = deduplicate_phrases(keywords)

    print(f"✅ Final keywords ({len(deduped_keywords)}): {deduped_keywords}")
    return comments, deduped_keywords


# ------------------------
# KEYWORD DEDUPLICATION
# ------------------------

def deduplicate_phrases(phrases, threshold=0.85):
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    embeddings = model.encode(phrases)
    sim_matrix = cosine_similarity(embeddings)

    keep = []
    seen = set()
    for i, phrase in enumerate(phrases):
        if i in seen:
            continue
        group = [j for j in range(len(phrases)) if sim_matrix[i][j] >= threshold]
        seen.update(group)
        keep.append(phrase)
    return keep


# ------------------------
# EMBEDDING + MATCHING
# ------------------------

def normalize(text):
    """Lowercase and remove punctuation for consistent matching."""
    return re.sub(r"[^\w\s]", "", text.lower().strip())


def embed_and_match(df, keywords, model_name=EMBEDDING_MODEL_NAME, threshold=0.5):
    """Embed comments and keywords, compute cosine similarity, and return matches."""
    comments = df["text"].astype(str).tolist()
    norm_comments = [normalize(c) for c in comments]
    norm_keywords = [normalize(k) for k in keywords]

    model = SentenceTransformer(model_name)
    comment_embeddings = model.encode(norm_comments, convert_to_tensor=True).cpu().numpy()
    keyword_embeddings = model.encode(norm_keywords, convert_to_tensor=True).cpu().numpy()

    sim_matrix = cosine_similarity(comment_embeddings, keyword_embeddings)

    all_keywords = []
    for i, comment in enumerate(comments):
        matched_keywords = []
        for j, keyword in enumerate(keywords):
            if sim_matrix[i][j] >= threshold:
                matched_keywords.append(keyword)
        all_keywords.append(sorted(matched_keywords))

    df["keywords"] = all_keywords
    return df


def run_embedding_pipeline(keywords):
    print("📥 Loading final_comments.csv and keywords.csv...")

    df_comments = pd.read_csv("final_comments.csv")

    print(f"✅ Loaded {len(df_comments)} comments and {len(keywords)} keywords.")
    print("🔍 Running embedding similarity...")
    result_df = embed_and_match(df_comments, keywords, threshold=0.5)

    print("💾 Saving results to comment_keyword_map.json...")

    json_records = result_df[["text", "sentiment", "keywords"]].to_dict(orient="records")
    lowercased_records = [
        {
            "text": record["text"].lower(),
            "sentiment": (record["sentiment"] or "").lower(),
            "keywords": [kw.lower() for kw in record["keywords"]]
        }
        for record in json_records
    ]
    with open("comment_keyword_map.json", "w", encoding="utf-8") as f:
        json.dump(lowercased_records, f, indent=2, ensure_ascii=False)

    print("📤 Loading records into the database...")
    load_comments_to_db("comment_keyword_map.json")

    print("✅ Done.")


# ------------------------
# GRAPH BUILDING (DB-native)
# ------------------------

def build_graph():
    print("🔍 Building graph directly from DB...")
    graph = build_graph_from_db()
    graph = add_llm_links(graph)   # optional enrichment
    save_graph_to_json(graph)

    print("📤 Loading graph into the database...")
    load_graph_data_to_db()


# ------------------------
# ENTRY POINT
# ------------------------

if __name__ == "__main__":
    comments, keywords = extract_keywords_llm()
    run_embedding_pipeline(keywords)
    build_graph()