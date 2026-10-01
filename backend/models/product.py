from typing import List, Optional
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    description: str
    image: str

class ProductWithScore(Product):
    similarity: float = Field(..., description="Similarity percentage score between 0.0 and 100.0")

class TextSearchRequest(BaseModel):
    query: str = Field(..., example="black running shoes")
    top_k: Optional[int] = Field(10, ge=1, le=30)

class SearchResponse(BaseModel):
    query: Optional[str] = None
    has_image: bool = False
    count: int
    results: List[ProductWithScore]
