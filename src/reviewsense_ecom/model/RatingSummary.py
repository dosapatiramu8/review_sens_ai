from typing import List, Dict

from groq import BaseModel


class RatingSummary(BaseModel):
    ratings_count: int
    average_rating: float
    rating_distribution: Dict[str, int]
    total_reviews: List[str]
