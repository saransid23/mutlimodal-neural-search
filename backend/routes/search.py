import io
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from PIL import Image

from backend.models.product import SearchResponse, TextSearchRequest
from backend.services.search_service import get_search_service

router = APIRouter(prefix="/search", tags=["Search"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image_file(file: UploadFile, contents: bytes):
    """Validate file type and file size."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.content_type}'. Please upload JPG, JPEG, or PNG images."
        )
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 5MB."
        )

@router.post("/text", response_model=SearchResponse)
async def text_search(payload: TextSearchRequest):
    """Perform text-based vector search using CLIP text embeddings."""
    query_str = payload.query.strip()
    if not query_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a non-empty search query."
        )

    service = get_search_service()
    results = service.search_by_text(query=query_str, top_k=payload.top_k)
    return SearchResponse(
        query=query_str,
        has_image=False,
        count=len(results),
        results=results
    )

@router.post("/image", response_model=SearchResponse)
async def image_search(image: UploadFile = File(...), top_k: int = Form(10)):
    """Perform image-based vector search using CLIP image embeddings."""
    if not image or not image.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a valid image file."
        )

    contents = await image.read()
    validate_image_file(image, contents)

    try:
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process image file: {str(e)}"
        )

    service = get_search_service()
    results = service.search_by_image(image=pil_image, top_k=top_k)
    return SearchResponse(
        query=None,
        has_image=True,
        count=len(results),
        results=results
    )

@router.post("/multimodal", response_model=SearchResponse)
async def multimodal_search(
    query: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    top_k: int = Form(10),
    image_weight: float = Form(0.6),
    text_weight: float = Form(0.4)
):
    """Perform combined multimodal (Image + Text) search using weighted CLIP embeddings."""
    query_clean = query.strip() if query else None
    pil_image = None

    if image and image.filename:
        contents = await image.read()
        validate_image_file(image, contents)
        try:
            pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process uploaded image: {str(e)}"
            )

    if pil_image is None and not query_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a search query or upload an image."
        )

    service = get_search_service()
    results = service.search_multimodal(
        image=pil_image,
        text=query_clean,
        top_k=top_k,
        image_weight=image_weight,
        text_weight=text_weight
    )
    return SearchResponse(
        query=query_clean,
        has_image=(pil_image is not None),
        count=len(results),
        results=results
    )
