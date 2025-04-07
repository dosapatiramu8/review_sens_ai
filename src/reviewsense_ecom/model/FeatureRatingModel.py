from dataclasses import dataclass


@dataclass
class FeatureRating:
    average_rating: float = 0.0
    review_count: int = 0
    positive_count: int = 0
    negative_count: int = 0
