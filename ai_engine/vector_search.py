import os
import faiss
import numpy as np

def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build a FAISS IndexFlatIP (Inner Product) index for normalized embeddings.
    Inner Product on unit vectors equals Cosine Similarity.
    """
    if embeddings.ndim == 1:
        embeddings = np.expand_dims(embeddings, axis=0)

    embeddings = embeddings.astype(np.float32)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    return index

def save_faiss_index(index: faiss.Index, filepath: str) -> None:
    """Save FAISS index to a local file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    faiss.write_index(index, filepath)
    print(f"[Vector Search] FAISS index saved to {filepath}")

def load_faiss_index(filepath: str) -> faiss.Index:
    """Load FAISS index from a local file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"FAISS index file not found at {filepath}")
    index = faiss.read_index(filepath)
    print(f"[Vector Search] FAISS index loaded from {filepath} (total vectors: {index.ntotal})")
    return index

def search_index(index: faiss.Index, query_vector: np.ndarray, top_k: int = 10):
    """
    Search FAISS index with a query vector.
    Returns:
        indices (list of int): Matching product index IDs
        scores (list of float): Similarity scores (0.0 to 100.0%)
    """
    if query_vector.ndim == 1:
        query_vector = np.expand_dims(query_vector, axis=0)

    query_vector = query_vector.astype(np.float32)

    # Search top K nearest neighbors
    top_k = min(top_k, index.ntotal)
    distances, indices = index.search(query_vector, top_k)

    raw_scores = distances[0]
    matched_indices = indices[0]

    # Convert inner product score (-1.0 to 1.0) into similarity percentage
    similarity_scores = []
    for score in raw_scores:
        # Scale cosine similarity (-1.0..1.0) into percentage (0%..100%)
        # For normalized vectors, dot product score > 0 typically means positive alignment
        pct = max(0.0, min(100.0, float(score) * 100.0))
        similarity_scores.append(round(pct, 1))

    return matched_indices.tolist(), similarity_scores
