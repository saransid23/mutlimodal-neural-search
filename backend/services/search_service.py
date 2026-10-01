import os
import json
from typing import List, Dict, Any, Optional
from PIL import Image

from ai_engine.embedding import (
    get_text_embedding,
    get_image_embedding,
    get_multimodal_embedding
)
from ai_engine.vector_search import load_faiss_index, search_index
from ai_engine.index import build_product_embeddings_and_index, PRODUCTS_JSON_PATH, FAISS_INDEX_SAVE_PATH

class SearchService:
    def __init__(self):
        self.products: List[Dict[str, Any]] = []
        self.products_by_id: Dict[int, Dict[str, Any]] = {}
        self.index = None
        self._load_products()
        self._load_or_build_index()

    def _load_products(self):
        """Load product metadata from products.json."""
        if os.path.exists(PRODUCTS_JSON_PATH):
            with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
                self.products = json.load(f)
            self.products_by_id = {p["id"]: p for p in self.products}
            print(f"[SearchService] Loaded {len(self.products)} products from json.")
        else:
            raise FileNotFoundError(f"products.json missing at {PRODUCTS_JSON_PATH}")

    def _load_or_build_index(self):
        """Load existing FAISS index or build it if missing."""
        if os.path.exists(FAISS_INDEX_SAVE_PATH):
            try:
                self.index = load_faiss_index(FAISS_INDEX_SAVE_PATH)
            except Exception as e:
                print(f"[SearchService] Error loading index ({e}). Rebuilding...")
                self.index = build_product_embeddings_and_index()
        else:
            print("[SearchService] FAISS index file not found. Building now...")
            self.index = build_product_embeddings_and_index()

    def search_by_text(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search products using text query embedding."""
        if not query or not query.strip():
            return []
        text_emb = get_text_embedding(query)
        indices, scores = search_index(self.index, text_emb, top_k=top_k)
        
        results = []
        for idx, score in zip(indices, scores):
            if 0 <= idx < len(self.products):
                product_copy = dict(self.products[idx])
                product_copy["similarity"] = score
                results.append(product_copy)
        return results

    def search_by_image(self, image: Image.Image, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search products using uploaded image embedding."""
        image_emb = get_image_embedding(image)
        indices, scores = search_index(self.index, image_emb, top_k=top_k)
        
        results = []
        for idx, score in zip(indices, scores):
            if 0 <= idx < len(self.products):
                product_copy = dict(self.products[idx])
                product_copy["similarity"] = score
                results.append(product_copy)
        return results

    def search_multimodal(
        self,
        image: Optional[Image.Image] = None,
        text: Optional[str] = None,
        top_k: int = 10,
        image_weight: float = 0.6,
        text_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """Search products using combined weighted image + text embedding."""
        if image is None and not (text and text.strip()):
            raise ValueError("At least an image or a text query must be provided.")

        multimodal_emb = get_multimodal_embedding(
            image=image,
            text=text,
            image_weight=image_weight,
            text_weight=text_weight
        )
        indices, scores = search_index(self.index, multimodal_emb, top_k=top_k)
        
        results = []
        for idx, score in zip(indices, scores):
            if 0 <= idx < len(self.products):
                product_copy = dict(self.products[idx])
                product_copy["similarity"] = score
                results.append(product_copy)
        return results

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Return all products in dataset."""
        return self.products

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Return single product details by ID."""
        return self.products_by_id.get(product_id)

# Global singleton service instance
search_service_instance: Optional[SearchService] = None

def get_search_service() -> SearchService:
    global search_service_instance
    if search_service_instance is None:
        search_service_instance = SearchService()
    return search_service_instance
