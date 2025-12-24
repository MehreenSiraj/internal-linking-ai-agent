from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_pages(pages):
    texts = [p["content"][:2000] for p in pages]  # cap for speed
    embeddings = model.encode(texts)
    return embeddings

def cluster_pages(embeddings, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    
    # Calculate silhouette score (measure of cluster cohesion)
    # Range: -1 (bad) to 1 (excellent), typically 0.3+ is acceptable
    silhouette_avg = silhouette_score(embeddings, labels)
    
    return labels, silhouette_avg
