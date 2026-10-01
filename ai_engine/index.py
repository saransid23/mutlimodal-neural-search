import os
import json
import numpy as np
from PIL import Image
from ai_engine.embedding import get_image_embedding, get_text_embedding, normalize_embedding
from ai_engine.vector_search import build_faiss_index, save_faiss_index

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRODUCTS_JSON_PATH = os.path.join(PROJECT_ROOT, "backend", "data", "products.json")
EMBEDDINGS_SAVE_PATH = os.path.join(PROJECT_ROOT, "ai_engine", "product_embeddings.npy")
FAISS_INDEX_SAVE_PATH = os.path.join(PROJECT_ROOT, "ai_engine", "products.index")

def build_product_embeddings_and_index():
    """
    Reads products.json, generates CLIP embeddings for each product image
    (combined with text description for rich semantic representation),
    saves embeddings to .npy, and builds/saves FAISS index.
    """
    print("==================================================", flush=True)
    print("Building Product Embeddings and FAISS Index...", flush=True)
    print("==================================================", flush=True)

    if not os.path.exists(PRODUCTS_JSON_PATH):
        raise FileNotFoundError(f"Products file not found at {PRODUCTS_JSON_PATH}")

    with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    embeddings_list = []

    for idx, product in enumerate(products):
        product_id = product.get("id")
        name = product.get("name")
        image_rel_path = product.get("image")

        # Resolve image path relative to frontend/ or project root
        image_abs_path = os.path.join(PROJECT_ROOT, "frontend", image_rel_path)
        if not os.path.exists(image_abs_path):
            # Try direct relative path
            image_abs_path = os.path.join(PROJECT_ROOT, image_rel_path)

        print(f"[{idx+1}/{len(products)}] Processing Product ID {product_id}: '{name}'...", flush=True)

        # Generate image embedding
        if os.path.exists(image_abs_path):
            img = Image.open(image_abs_path)
            img_emb = get_image_embedding(img)
        else:
            print(f"  [Warning] Image not found at {image_abs_path}. Falling back to text embedding.", flush=True)
            img_emb = None

        # Generate text embedding for name + description
        text_query = f"{product.get('category')} {name} {product.get('description')}"
        txt_emb = get_text_embedding(text_query)

        # Multi-feature representation for product indexing: 70% image features + 30% textual metadata
        if img_emb is not None:
            combined = (img_emb * 0.7) + (txt_emb * 0.3)
            final_emb = normalize_embedding(combined)
        else:
            final_emb = txt_emb

        embeddings_list.append(final_emb)

    # Convert to numpy array
    embeddings_matrix = np.vstack(embeddings_list).astype(np.float32)

    # Save embeddings to .npy file
    np.save(EMBEDDINGS_SAVE_PATH, embeddings_matrix)
    print(f"Saved product embeddings matrix of shape {embeddings_matrix.shape} to {EMBEDDINGS_SAVE_PATH}", flush=True)

    # Build FAISS index
    index = build_faiss_index(embeddings_matrix)

    # Save FAISS index
    save_faiss_index(index, FAISS_INDEX_SAVE_PATH)

    print("==================================================", flush=True)
    print("FAISS Index Build Completed Successfully!", flush=True)
    print("==================================================", flush=True)
    return index

if __name__ == "__main__":
    build_product_embeddings_and_index()
