import numpy as np
import torch
from PIL import Image
from ai_engine.clip_model import get_clip_model, get_clip_processor, get_device

def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """L2 normalize a numpy embedding array."""
    if embedding.ndim == 1:
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding.astype(np.float32)
        return (embedding / norm).astype(np.float32)
    else:
        norm = np.linalg.norm(embedding, axis=-1, keepdims=True)
        norm = np.where(norm == 0, 1.0, norm)
        return (embedding / norm).astype(np.float32)

def _extract_feature_tensor(features) -> torch.Tensor:
    """Extract 2D feature tensor [batch, dim] from model outputs."""
    if isinstance(features, torch.Tensor):
        return features
    if hasattr(features, "image_embeds") and features.image_embeds is not None:
        return features.image_embeds
    if hasattr(features, "text_embeds") and features.text_embeds is not None:
        return features.text_embeds
    if hasattr(features, "pooler_output") and features.pooler_output is not None:
        return features.pooler_output
    return features[0]

def get_image_embedding(image: Image.Image) -> np.ndarray:
    """Generate an L2-normalized 512-dim CLIP embedding for a PIL Image."""
    model = get_clip_model()
    processor = get_clip_processor()
    device = get_device()

    # Ensure RGB format
    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        features = model.get_image_features(**inputs)
        image_tensor = _extract_feature_tensor(features)

    embedding = image_tensor.cpu().numpy().squeeze(0)
    return normalize_embedding(embedding)

def get_text_embedding(text: str) -> np.ndarray:
    """Generate an L2-normalized 512-dim CLIP embedding for a text string."""
    model = get_clip_model()
    processor = get_clip_processor()
    device = get_device()

    inputs = processor(text=[text], return_tensors="pt", padding=True, truncation=True).to(device)

    with torch.no_grad():
        features = model.get_text_features(**inputs)
        text_tensor = _extract_feature_tensor(features)

    embedding = text_tensor.cpu().numpy().squeeze(0)
    return normalize_embedding(embedding)

def get_multimodal_embedding(
    image: Image.Image = None,
    text: str = None,
    image_weight: float = 0.6,
    text_weight: float = 0.4
) -> np.ndarray:
    """
    Combine image and text embeddings using weighted sum:
    final_embedding = (image_embedding * image_weight) + (text_embedding * text_weight)
    Then L2 normalize before FAISS search.
    """
    img_emb = get_image_embedding(image) if image is not None else None
    txt_emb = get_text_embedding(text) if (text and text.strip()) else None

    if img_emb is not None and txt_emb is not None:
        combined = (img_emb * image_weight) + (txt_emb * text_weight)
        return normalize_embedding(combined)
    elif img_emb is not None:
        return img_emb
    elif txt_emb is not None:
        return txt_emb
    else:
        raise ValueError("At least one of image or text must be provided for multimodal embedding generation.")
