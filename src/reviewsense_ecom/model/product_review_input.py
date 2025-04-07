from typing import List, Optional

from pydantic import BaseModel, Field


class ProductReviewInput(BaseModel):
    """Input model for product review processing"""
    product_id: str = Field(..., description="Unique identifier for the product")
    features: List[str] = Field(..., description="Features to analyze")
    new_review: Optional[str] = Field(default=None, description="Optional new review to add")
    is_rating_evaluation_required: bool = Field(
        default=True,
        description="Flag to determine if rating evaluation is needed"
    )
    new_rating: int = Field(..., description="Rating for the product")

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "product_id": "",
                "features": ["camera", "battery", "display", "design"],
                "new_review": "",
                "is_rating_evaluation_required": True,
                "new_rating": 0,
            }
        }
