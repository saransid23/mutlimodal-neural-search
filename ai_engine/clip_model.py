import torch
from transformers import CLIPProcessor, CLIPModel

MODEL_NAME = "openai/clip-vit-base-patch32"

_model = None
_processor = None
_device = None

def get_device() -> torch.device:
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device

def get_clip_model():
    """Singleton getter for the pretrained CLIP model."""
    global _model
    if _model is None:
        device = get_device()
        print(f"[AI Engine] Loading CLIP model ({MODEL_NAME}) on {device}...", flush=True)
        _model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
        _model.eval()
        print("[AI Engine] CLIP model loaded successfully.", flush=True)
    return _model

def get_clip_processor():
    """Singleton getter for the CLIP processor."""
    global _processor
    if _processor is None:
        print(f"[AI Engine] Loading CLIP processor ({MODEL_NAME})...", flush=True)
        _processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        print("[AI Engine] CLIP processor loaded successfully.", flush=True)
    return _processor
