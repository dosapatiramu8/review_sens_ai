from typing import Dict, Optional


class FeatureUpdater:
    def __init__(self, product_data: Optional[Dict] = None):
        if product_data is None:
            product_data = {}

        self.product_data = product_data
        self.product_data.setdefault("total_reviews", 0)
        self.product_data.setdefault("features", {})
        self.product_data.setdefault("ratings_distribution", {str(i): 0 for i in range(1, 6)})
        self.product_data.setdefault("overall_rating", 0.0)

    def update_feature_ratings(self, feature_data: Dict[str, Dict[str, Optional[float]]],
                               new_overall_rating: int) -> Dict:
        features = self.product_data.get("features", {})
        ratings_distribution = self.product_data.get("ratings_distribution", {str(i): 0 for i in range(1, 6)})
        existing_total_reviews = self.product_data.get("total_reviews", 0)
        current_overall_rating = self.product_data.get("overall_rating", 0.0)

        for feature, new_data in feature_data.items():
            if feature not in features:
                features[feature] = {
                    "average_rating": 0.0,
                    "review_count": 0,
                    "positive_count": 0,
                    "negative_count": 0
                }
            current_feature = features[feature]
            existing_review_count = current_feature["review_count"]

            M = 4.5

            C = max(2, 10 - (existing_review_count // 20))  # Reduce prior influence faster

            # if existing_review_count < 5:
            #     C = 5
            # elif existing_review_count < 50:
            #     C = 10
            # elif existing_review_count < 500:
            #     C = 15
            # else:
            #     C = 20

            new_ratings = new_data.get("ratings", [])
            new_rating = sum(new_ratings) / len(new_ratings) if new_ratings else 0
            new_positive = new_data.get("positive_count", 0) or 0
            new_negative = new_data.get("negative_count", 0) or 0

            # Apply the Bayesian Average Formula
            new_average_rating = (
                                         (current_feature["average_rating"] * existing_review_count) + (
                                         C * M) + new_rating
                                 ) / (existing_review_count + C + 1) if existing_review_count > 0 else new_rating

            print(f"{new_average_rating}+--------------------------$$$----------------")

            features[feature]["average_rating"] = round(new_average_rating, 1)
            features[feature]["review_count"] += 1
            features[feature]["positive_count"] += new_positive
            features[feature]["negative_count"] += new_negative

        ratings_distribution[str(new_overall_rating)] += 1

        updated_total_reviews = existing_total_reviews + 1
        new_overall_rating = (
                                     (current_overall_rating * existing_total_reviews) + new_overall_rating
                             ) / updated_total_reviews if existing_total_reviews > 0 else new_overall_rating

        self.product_data["features"] = features
        self.product_data["ratings_distribution"] = ratings_distribution
        self.product_data["overall_rating"] = round(new_overall_rating, 1)
        self.product_data["total_reviews"] = updated_total_reviews

        return self.product_data