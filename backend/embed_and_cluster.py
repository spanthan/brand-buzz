import pandas as pd
import numpy as np
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from textblob import TextBlob
from collections import defaultdict
import json

def extract_keywords():

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

if __name__ == "__main__":
    extract_keywords()
    create_db()
