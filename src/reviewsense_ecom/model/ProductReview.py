from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from pydantic import Field


@dataclass
class ProductReview:
    # id: Optional[ObjectId] = None
    product_id: str = ""
    review: Optional[str] = Field(default=None, max_length=5000, description="Review text")
    rating: float = 0.0
    # features: List[Dict[str, FeatureSentiment]] = field(default_factory=list)
    features: List[Dict[str, Dict[str, Any]]] = field(default_factory=list)
