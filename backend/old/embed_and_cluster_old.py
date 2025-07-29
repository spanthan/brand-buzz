import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
import matplotlib.pyplot as plt
import ollama

def embed_and_cluster_comments():
    # === STEP 1: Load your filtered comments ===
    print(f'Loading Final Comments')
    df = pd.read_csv("final_comments.csv")

    # === STEP 2: Generate Embeddings ===
    print(f'Generating Embeddings')
    model = SentenceTransformer("thenlper/gte-large")  # local, fast, semantic
    df["embedding"] = df["text"].apply(lambda x: model.encode(x).tolist())

    # Convert to matrix
    embedding_matrix = np.vstack(df["embedding"].to_numpy())

    # === STEP 3: (Optional) Dimensionality Reduction with UMAP ===
    print(f'Performing Dimensionality Reduction')
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
    reduced_embeddings = reducer.fit_transform(embedding_matrix)

    # === STEP 4: Cluster with HDBSCAN ===
    print(f'Clustering with HDBSCAN')
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
    df["cluster"] = clusterer.fit_predict(reduced_embeddings)

    # === STEP 5: Visualize clusters (optional) ===
    plt.figure(figsize=(10, 6))
    plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=df["cluster"], cmap="tab10", s=10)
    plt.title("HDBSCAN Clustering of Comment Embeddings")
    plt.xlabel("UMAP-1")
    plt.ylabel("UMAP-2")
    plt.colorbar(label="Cluster ID")
    plt.show()

    # === STEP 6: Save results for labeling ===
    print(f'Saving Results for Labeling')

    df.to_csv("clustered_comments.csv", index=False)
    print(f"Found {df['cluster'].nunique()} clusters (including noise)")


def label_clusters_with_llm():
    # === Load clustered data ===
    df = pd.read_csv("clustered_comments.csv")

    # === Helper: Generate prompt for a cluster ===
    def generate_prompt(cluster_comments):
        sample = "\n".join(f"- {text}" for text in cluster_comments)
        prompt = (
            "You are analyzing a group of social media comments about a skincare product.\n"
            "These comments have been grouped together using semantic similarity.\n"
            "Your job is to pick out a common **themes** in just a few words (e.g., 'Eye irritation', 'Makeup removal', 'Double cleansing method').\n\n"
            "Here are the comments:\n" + sample + "\n\n"
            "What are the shared common key words or themes?"
            "Only return the key words/themes and nothing else"
        )
        return prompt

    # === Ask LLM for each cluster ===
    theme_labels = {}
    unique_clusters = sorted(df["cluster"].unique())
    if -1 in unique_clusters:
        unique_clusters.remove(-1)  # Skip noise

    for cluster_id in unique_clusters:
        cluster_comments = df[df["cluster"] == cluster_id]["text"].tolist()
        sample = cluster_comments[:10]

        prompt = generate_prompt(sample)
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )

        theme = response["message"]["content"].strip()
        theme_labels[cluster_id] = theme
        print(f"Cluster {cluster_id} → {theme}")

    # === Add theme labels back to the dataframe ===
    df["theme_name"] = df["cluster"].apply(lambda c: theme_labels.get(c, "Noise"))

    # === Save updated results ===
    df[["text", "cluster", "theme_name"]].to_csv("clustered_final_comments.csv", index=False)
    print("Labeled themes saved to clustered_final_comments.csv")

def only_get_text_cluster():

    df = pd.read_csv("clustered_comments.csv")
    grouped = df[["text", "cluster"]].groupby("cluster")["text"].apply(list).reset_index()
    grouped.to_json("comments_grouped_by_cluster.json", orient="records", indent=2, force_ascii=False)


if __name__ == "__main__":
    embed_and_cluster_comments()
    only_get_text_cluster()
    label_clusters_with_llm()