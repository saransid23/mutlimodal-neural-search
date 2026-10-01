from typing import List
from fastapi import APIRouter, HTTPException, status
from backend.models.product import Product
from backend.services.search_service import get_search_service

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[Product])
async def get_all_products():
    """Retrieve all available products from dataset."""
    service = get_search_service()
    return service.products

@router.get("/{product_id}", response_model=Product)
async def get_product_details(product_id: int):
    """Retrieve a single product by its unique product_id."""
    service = get_search_service()
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    return product
