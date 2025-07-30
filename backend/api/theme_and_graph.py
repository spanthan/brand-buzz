import pandas as pd
import ollama
import re
from collections import defaultdict, Counter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import ollama
import json
from itertools import combinations

from sentiment_analysis import *
from db_loader import *

EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
SIMILARITY_THRESHOLD = 0.5      # Keywords above this threshold are accepted
BORDERLINE_THRESHOLD = 0.4      # Keywords in this range go through LLM

def run_llm(prompt, model="llama3"):

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content'].strip()

def process_llm_response(response):
    parts = response.lower().split("\n\n")
    for part in parts:
        if part.strip().startswith('"') and part.strip().endswith('"'):
            return part.strip()
    return None

def deduplicate_phrases(phrases, threshold=0.85):
    model = SentenceTransformer('all-MiniLM-L6-v2')
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

def extract_keywords_llm_helper(comments):
    print("🔍 Extracting keywords with LLM...")
    with open(f"prompts/keyword_prompt.txt", "r", encoding="utf-8") as file:
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
    
def normalize(text):
    """Lowercase and remove punctuation for consistent matching."""
    return re.sub(r"[^\w\s]", "", text.lower().strip())

# ------------------------
# MAIN FUNCTION
# ------------------------

def embed_and_match(df, keywords, model_name='all-MiniLM-L6-v2', threshold=0.5):
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

# ------------------------
# PIPELINE ENTRY POINT
# ------------------------

def run_embedding_pipeline(keywords):
    print("📥 Loading final_comments.csv and keywords.csv...")

    df_comments = pd.read_csv("final_comments.csv")

    print(f"✅ Loaded {len(df_comments)} comments and {len(keywords)} keywords.")
    print("🔍 Running embedding similarity...")
    result_df = embed_and_match(df_comments, keywords, threshold=0.5)

    print("💾 Saving results to comment_keyword_map.json...")

    # Save to JSON with desired format
    json_records = result_df[["text", "sentiment", "keywords"]].to_dict(orient="records")
    lowercased_records = [
    {
        "text": record["text"].lower(),
        "sentiment": record["sentiment"].lower(),
        "keywords": [kw.lower() for kw in record["keywords"]]
    }
    for record in json_records
]
    with open("comment_keyword_map.json", "w", encoding="utf-8") as f:
        json.dump(lowercased_records, f, indent=2, ensure_ascii=False)
    
    print("📤 Loading records into the database...")
    load_comments_to_db("comment_keyword_map.json")

    print("✅ Done.")

def preprocess_comments(comments):
    theme_comment_counts = Counter()
    theme_sentiment_counts = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})
    co_occurrence_counts = Counter()

    for comment in comments:
        sentiment = comment["sentiment"]
        keywords = [kw.strip().lower() for kw in comment.get("keywords", []) if kw.strip()]
        unique_keywords = list(set(keywords))

        for kw in unique_keywords:
            theme_comment_counts[kw] += 1
            theme_sentiment_counts[kw][sentiment] += 1

        for kw1, kw2 in combinations(sorted(unique_keywords), 2):
            co_occurrence_counts[(kw1, kw2)] += 1

    return theme_comment_counts, theme_sentiment_counts, co_occurrence_counts

def build_nodes(theme_comment_counts,
                theme_sentiment_counts,
                total_comments):
    nodes = []
    for theme, count in theme_comment_counts.items():
        sentiment_data = theme_sentiment_counts[theme]
        dominant_sentiment = max(sentiment_data.items(), key=lambda x: x[1])[0]
        weight = round(count, 3)
        nodes.append({
            "keyword": theme,
            "weight": weight,
            "sentiment": dominant_sentiment
        })
    return nodes

def build_links(co_occurrence_counts):
    links = []
    for (kw1, kw2), value in co_occurrence_counts.items():
        links.append({
            "source": kw1,
            "target": kw2,
            "value": value
        })
    return links

def generate_theme_graph(comments):
    total_comments = len(comments)
    theme_counts, sentiment_counts, co_occurrence = preprocess_comments(comments)
    nodes = build_nodes(theme_counts, sentiment_counts, total_comments)
    links = build_links(co_occurrence)
    return {"nodes": nodes, "links": links}

def add_llm_links(graph, min_links=4, top_k=10):
    model = SentenceTransformer('all-MiniLM-L6-v2')  # small and fast
    nodes = graph['nodes']
    links = graph['links']

    # Build a map of theme → current connections
    connected = defaultdict(set)
    for link in links:
        connected[link['source']].add(link['target'])
        connected[link['target']].add(link['source'])

    all_themes = [node["keyword"] for node in nodes]
    theme_index = {t: i for i, t in enumerate(all_themes)}

    # Embed all themes once
    embeddings = model.encode(all_themes, convert_to_tensor=True)

    # Add synthetic links
    new_links = []
    for node in nodes:
        theme = node["keyword"]
        current_neighbors = connected[theme]

        if len(current_neighbors) >= min_links:
            continue  # already has enough connections

        # Compute cosine similarity to all other nodes
        idx = theme_index[theme]
        sims = cosine_similarity(
            embeddings[idx].cpu().numpy().reshape(1, -1),
            embeddings.cpu().numpy()
        ).flatten()

        # Sort by similarity, exclude self and already-linked
        sorted_indices = np.argsort(-sims)
        count = 0
        for i in sorted_indices:
            candidate = all_themes[i]
            if candidate == theme or candidate in current_neighbors:
                continue
            new_links.append({
                "source": theme,
                "target": candidate,
                "value": 0.5  # mark it as LLM-based
            })
            connected[theme].add(candidate)
            # connected[candidate].add(theme)
            count += 1
            if len(connected[theme]) >= min_links:
                break

    print(f"🔗 Added {len(new_links)} LLM-based links.")
    graph['links'].extend(new_links)
    return graph

def save_graph_to_json(graph, path = "theme_graph.json"):
    with open(path, "w") as f:
        json.dump(graph, f, indent=2)
    print(f"✅ Graph saved with {len(graph['nodes'])} nodes and {len(graph['links'])} links.")

def build_graph():
    with open("comment_keyword_map.json", "r", encoding="utf-8") as f:
        comments = json.load(f)
    graph = generate_theme_graph(comments)
    graph = add_llm_links(graph)
    save_graph_to_json(graph)


if __name__ == "__main__":
    comments, keywords = extract_keywords_llm()
    run_embedding_pipeline(keywords)
    build_graph()
    load_graph_data_to_db()

