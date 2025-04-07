from typing import List, Dict, Optional

from src.reviewsense_ecom.mongo.mongo_db_config import get_db_connection
from src.reviewsense_ecom.service.ReviewRater import ReviewRater


class ReviewService:
    """Service class for handling product reviews"""

    def __init__(self):

        """
        Initialize the review service with MongoDB connection.
        """

        # Vector-based processing components
        self.rater = ReviewRater()

    def _get_collection(self, collection_name):
        """Returns the requested MongoDB collection."""
        return get_db_connection(collection_name)

    def get_review_by_feature(self, product_id, feature):
        """
        Fetch reviews from MongoDB based on `product_id` and `feature`
        """
        collection = self._get_collection("productReviews")

        query = {"product_id": str(product_id)}
        projection = {"_id": 0, "review": 1, "features": 1}

        reviews = collection.find(query, projection)
        list(collection.find(query, projection))

        result = []
        for review in reviews:
            if feature.lower() == "overall":
                result.append(review.get("review", ""))
            else:
                features = review.get("features", [])
                for feature_dict in features:
                    if feature in feature_dict:
                        feature_data = feature_dict[feature]
                        result.extend(feature_data.get("positive", []))
                        result.extend(feature_data.get("negative", []))

        return result

    def get_full_review_by_feature(self, product_id, feature):
        """
        Fetch reviews from MongoDB based on product_id and feature.
        If the feature is present, return the 'review' field.
        """
        collection = self._get_collection("productReviews")

        query = {"product_id": str(product_id)}
        projection = {"_id": 0, "review": 1, "features": 1}

        reviews = collection.find(query, projection)

        result = []
        for review in reviews:
            if feature.lower() == "overall":
                result.append(review.get("review", ""))
            else:
                features = review.get("features", [])
                for feature_dict in features:
                    if feature in feature_dict:
                        result.append(review.get("review", ""))
                        break

        return result

    def get_percentage_by_feature(self, product_id, feature, collection_name="productFeatureRater"):
        """
        Retrieves positive and negative review counts along with average rating for a given product feature.
        """
        collection = self._get_collection(collection_name)

        query = {
            "product_id": str(product_id),
            f"features.{feature}": {"$exists": True}
        }
        projection = {
            "_id": 0,
            f"features.{feature}.positive_count": 1,
            f"features.{feature}.negative_count": 1,
            f"features.{feature}.average_rating": 1
        }

        document = collection.find_one(query, projection)

        if not document:
            return {"message": "No reviews found for this product and feature."}

        feature_data = document.get("features", {}).get(feature, {})
        positive_count = feature_data.get("positive_count", 0)
        negative_count = feature_data.get("negative_count", 0)
        average_rating = feature_data.get("average_rating", None)

        sum_reviews = positive_count + negative_count
        positive_percentage = float((positive_count / sum_reviews) * 100) if sum_reviews else 0
        negative_percentage = float((negative_count / sum_reviews) * 100) if sum_reviews else 0

        return {
            "positive_percentage": f"{positive_percentage}%",
            "negative_percentage": f"{negative_percentage}%",
            "average_rating": average_rating
        }

    def fetch_feature_ratings(self, reviews_by_feature: List[Dict[str, str]]) -> Dict[str, Dict[str, Optional[float]]]:
        return self.rater.generate_feature_ratings(reviews_by_feature)
