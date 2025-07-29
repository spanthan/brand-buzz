import pandas as pd
import numpy as np
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from textblob import TextBlob
from collections import defaultdict
import json
import ollama
import re
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict, Counter
from itertools import combinations


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

def extract_keywords_llm():
    print("📥 Loading final_comments.csv")

    df = pd.read_csv("final_comments.csv")
    comments = df["text"].dropna().astype(str).tolist()

    print(f"✅ Loaded {len(comments)} comments")

    print("🔍 Extracting keywords with LLM...")
    with open(f"prompts/keyword_prompt.txt", "r", encoding="utf-8") as file:
        template = file.read()
    prompt = template.format(comment_list = comments, length = 20)
    response = run_llm(prompt)
    keywords = process_llm_response(response)
    keywords = re.findall(r'"(.*?)"', keywords)
    print(keywords)

def extract_keywords_llm_one_by_one():
    print("📥 Loading final_comments.csv")

    df = pd.read_csv("final_comments.csv")
    comments = df["text"].dropna().astype(str).tolist()

    print(f"✅ Loaded {len(comments)} comments")

    print("🔍 Extracting keywords with LLM...")
    with open(f"prompts/keyword_prompt.txt", "r", encoding="utf-8") as file:
        template = file.read()

    comment_keywords = []
    for comment in comments:
        prompt = template.format(comment_text = comment)
        response = run_llm(prompt)
        keywords = process_llm_response(response)
        if keywords == None:
            keywords = []
        else:
            keywords = re.findall(r'"(.*?)"', keywords)
        comment_keywords.append(keywords)
    print("✅ Finished keyword extraction")

    df = df.loc[df["text"].notna()].copy()  # Align with filtered comments
    df["keywords"] = comment_keywords

    df.to_json("comments_with_keywords.json", orient="records", indent=2)
    print("💾 Saved to comments_with_keywords.json")

def extract_keywords_keybert():

    # === Step 1: Load Comments ===
    print("📥 Loading final_comments.csv")

    df = pd.read_csv("final_comments.csv")
    comments = df["text"].dropna().astype(str).tolist()

    print(f"✅ Loaded {len(comments)} comments")

    # === Step 2: Extract Keywords with KeyBERT ===
    print("🔍 Extracting keywords with KeyBERT...")
    kw_model = KeyBERT(model='all-MiniLM-L6-v2')

    comment_keywords = []
    for i, text in enumerate(comments):
        keyword_scores = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=10)
        
        filtered_keywords = [kw for kw, score in keyword_scores if score > 0.1]  # You control the threshold
        comment_keywords.append(filtered_keywords)


        if i % 50 == 0:
            print(f"  ➤ Processed {i}/{len(comments)} comments")

    print("✅ Finished keyword extraction")

    # === Step 3: Add keywords to DataFrame and save ===
    df = df.loc[df["text"].notna()].copy()  # Align with filtered comments
    df["keywords"] = comment_keywords

    df.to_csv("comments_with_keywords.csv", index=False)
    print("💾 Saved to comments_with_keywords.csv")

def create_db():
    # === Step 1: Load and Parse the Data ===
    df = pd.read_csv("comments_with_keywords.csv")

    # Convert keyword strings to actual lists (assuming they're stored like "['a', 'b']")
    df["keywords"] = df["keywords"].apply(eval)

    # === Step 2: Compute Sentiment ===
    def get_sentiment(text):
        try:
            return TextBlob(text).sentiment.polarity
        except:
            return 0.0

    df["sentiment"] = df["text"].apply(get_sentiment)

    # === Step 3: Aggregate by Theme ===
    theme_data = defaultdict(lambda: {"count": 0, "total_sentiment": 0.0, "comments": []})

    for _, row in df.iterrows():
        sentiment = row["sentiment"]
        text = row["text"]
        for keyword in row["keywords"]:
            theme_data[keyword]["count"] += 1
            theme_data[keyword]["total_sentiment"] += sentiment
            theme_data[keyword]["comments"].append(text)

    # === Step 4: Compute Weight and Avg Sentiment ===
    total_comments = len(df)
    records = []

    for theme, data in theme_data.items():
        count = data["count"]
        avg_sentiment = data["total_sentiment"] / count
        weight = count / total_comments
        records.append({
            "theme": theme,
            "average_sentiment": round(avg_sentiment, 3),
            "weight": round(weight, 3),
            "num_comments": count
        })

    # === Step 5: Save to CSV/JSON ===
    theme_df = pd.DataFrame(records)
    theme_df = theme_df.sort_values(by="weight", ascending=False)
    theme_df.to_csv("theme_sentiment_weight.csv", index=False)
    theme_df.to_json("theme_sentiment_weight.json", orient="records", indent=2)

    print("✅ Done! Saved results to theme_sentiment_weight.csv and .json")

def batch_list(keywords, batch_size= 20):
    return [keywords[i:i + batch_size] for i in range(0, len(keywords), batch_size)]

def build_grouping_prompt(batch) -> str:
    formatted = '\n'.join([f'Input: "{phrase}"' for phrase in batch])
    return formatted

def extract_canonical_themes_clustering():
    # 1. Get list of raw keywords
    print("📥 Loading comments_with_keywords.json")

    df = pd.read_json("comments_with_keywords.json", orient="records")

    all_keywords = []
    for keyword_list in df['keywords']:
        all_keywords.extend(keyword_list)

    unique_keywords = list(set(all_keywords))

    # Print each unique keyword
    for kw in unique_keywords:
        print(kw)

    print(f"✅ Loaded {len(unique_keywords)} unique keywords")

    # 2. Generate embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(unique_keywords)

    # 3. Cluster with DBSCAN using cosine distance
    clustering = DBSCAN(eps=0.35, min_samples=2, metric="cosine").fit(embeddings)
    labels = clustering.labels_  # -1 means outlier (no cluster)

    # 4. Group keywords by cluster
    clusters = defaultdict(list)
    for keyword, label in zip(unique_keywords, labels):
        clusters[label].append(keyword)
    
    for label, keywords in clusters.items():
        if label == -1:
            print(f"\n🧩 Outliers ({len(keywords)}):")
        else:
            print(f"\n🧠 Cluster {label} ({len(keywords)} keywords):")
        for kw in keywords:
            print(f"  - {kw}")

    # # 5. Choose canonical theme for each cluster
    # # TODO: maybe change this step a bit
    # canonical_map = {}
    # for label, keywords in clusters.items():
    #     if label == -1:
    #         # Treat outliers as their own canonical themes
    #         for kw in keywords:
    #             canonical_map[kw] = kw
    #     else:
    #         # Choose most frequent or shortest keyword as representative
    #         keyword_counts = Counter(keywords)
    #         canonical_theme = sorted(keyword_counts.items(), key=lambda x: (x[1], -len(x[0])), reverse=True)[0][0]
    #         for kw in keywords:
    #             canonical_map[kw] = canonical_theme

    # # 6. Output
    # print("Raw → Canonical theme mapping:\n")
    # for raw, canon in canonical_map.items():
    #     print(f'"{raw}" → "{canon}"')
    # model = SentenceTransformer('all-MiniLM-L6-v2')
    # embeddings = model.encode(unique_keywords)

    # # 2. Cluster themes (tune distance_threshold as needed)
    # clustering = AgglomerativeClustering(
    #                 n_clusters=None,
    #                 distance_threshold=0.3,
    #                 affinity='cosine',
    #                 linkage='average'
    #             )
    # labels = clustering.fit_predict(embeddings)

    # # 3. Build canonical theme mapping
    # from collections import defaultdict

    # canonical_theme_map = defaultdict(list)
    # for theme, label in zip(unique_keywords, labels):
    #     canonical_theme_map[label].append(theme)

    # # 4. Choose a representative theme (e.g. shortest) for each cluster

    # # Assuming you have a list of all matched phrases in comments
    # phrase_freq = Counter([...])  # You'll need to track how often each phrase appears

    # label_to_canonical = {}
    # for label, group in canonical_theme_map.items():
    #     most_common = max(group, key=lambda phrase: phrase_freq.get(phrase, 0))
    #     label_to_canonical[label] = most_common

    # # 5. Build reverse lookup: theme -> canonical
    # theme_to_canonical = {
    #     theme: label_to_canonical[label]
    #     for theme, label in zip(unique_keywords, labels)
    # }
    # print(theme_to_canonical)

def extract_canonical_themes():
    # 1. Get list of raw keywords
    print("📥 Loading comments_with_keywords.json")

    df = pd.read_json("comments_with_keywords.json", orient="records")

    all_keywords = []
    for keyword_list in df['keywords']:
        all_keywords.extend(keyword_list)

    unique_keywords = list(set(all_keywords))

    # Print each unique keyword
    for kw in unique_keywords:
        print(kw)

    print(f"✅ Loaded {len(unique_keywords)} unique keywords")

    with open(f"prompts/duplicate_prompt.txt", "r", encoding="utf-8") as file:
        template = file.read()

    canonical_map = {}

    print(f"\n🔍 Processing prompt...")
    prompt = template.format(formatted = unique_keywords)
    response = run_llm(prompt, model="mixtral")  # assumes this is already defined
    print(response)

    # try:
    #     mapping = json.loads(response)
    #     if not isinstance(mapping, dict):
    #         raise ValueError("LLM did not return a dictionary.")
    #     canonical_map.update(mapping)
    # except Exception as e:
    #     print(f"❌ Error parsing output: {e}")
    #     print("Raw response:", response)

    # print("\n✅ Canonical map generated.")
    # for original, canonical in canonical_map.items():
    #     print(f"{original} → {canonical}")

    # print(canonical_map)
    # return canonical_map

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
            "id": theme,
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

    all_themes = [node["id"] for node in nodes]
    theme_index = {t: i for i, t in enumerate(all_themes)}

    # Embed all themes once
    embeddings = model.encode(all_themes, convert_to_tensor=True)

    # Add synthetic links
    new_links = []
    for node in nodes:
        theme = node["id"]
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
            connected[candidate].add(theme)
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
    with open("comments_with_keywords.json", "r", encoding="utf-8") as f:
        comments = json.load(f)
    graph = generate_theme_graph(comments)
    graph = add_llm_links(graph)
    save_graph_to_json(graph)

if __name__ == "__main__":
    extract_keywords_llm()
    # create_db()
    # extract_canonical_themes()
    # build_graph()
    print()
