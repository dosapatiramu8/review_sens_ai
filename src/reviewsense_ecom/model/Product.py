from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict
from src.reviewsense_ecom.model.Constants import DATE_KEY
from src.reviewsense_ecom.model.FeatureRatingModel import FeatureRating


@dataclass
class Product:
    product_id: str
    category: str
    features: Dict[str, FeatureRating]
    ratings_distribution: Dict[str, int]
    overall_rating: float = 0.0
    total_reviews: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))  # Use timezone-aware UTC datetime
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_dict(cls, data):
        """Convert a dictionary from MongoDB to a Product instance."""

        # Handling 'created_at' and 'updated_at' safely
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")

        def parse_datetime(value):
            if isinstance(value, dict) and DATE_KEY in value:
                return datetime.fromisoformat(value[DATE_KEY].replace("Z", ""))
            elif isinstance(value, str):  # If it's a string (ISO format)
                return datetime.fromisoformat(value.replace("Z", ""))
            return None  # Return None if it's missing or invalid

        created_at = parse_datetime(created_at)
        updated_at = parse_datetime(updated_at)

        return cls(
            product_id=data.get("product_id", ""),
            category=data.get("category", ""),
            features={k: FeatureRating(**v) for k, v in data.get("features", {}).items()},
            ratings_distribution=data.get("ratings_distribution", {}),
            overall_rating=data.get("overall_rating", 0),
            total_reviews=data.get("total_reviews", 0),
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self):
        """Convert the data class to a dictionary for MongoDB insertion."""
        return {
            "product_id": self.product_id,
            "category": self.category,
            "features": {k: v.__dict__ if hasattr(v, '__dict__') else v for k, v in self.features.items()},
            "ratings_distribution": self.ratings_distribution,
            "overall_rating": self.overall_rating,
            "total_reviews": self.total_reviews,
            "created_at": {DATE_KEY: self.created_at.isoformat() + "Z"} if self.created_at else None,
            "updated_at": {DATE_KEY: self.updated_at.isoformat() + "Z"} if self.updated_at else None
        }
