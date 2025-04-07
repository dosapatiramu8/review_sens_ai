# router/ReviewRater.py
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np
from transformers import pipeline


class ReviewRater:
    """Class for generating feature-specific ratings based on sentiment analysis"""

    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")

    def generate_feature_ratings(self, reviews_by_feature: List[Dict[str, str]]) -> Dict[
        str, Dict[str, Optional[float]]]:
        feature_data = defaultdict(
            lambda: {"ratings": [], "positive_count": 0, "negative_count": 0, "neutral_count": 0}
        )

        for review_data in reviews_by_feature:
            feature = review_data.get("feature")
            sentiment = review_data.get("sentiment")
            confidence = float(review_data.get("confidence", 1))

            if not feature or not sentiment:
                continue

            if "positive" in sentiment:
                score = 3 + 2 * confidence
                print(f"confidence value for positive: {confidence}")
                feature_data[feature]["positive_count"] += 1
            elif "negative" in sentiment:
                score = 3 - 2 * confidence
                print(f"confidence value for negative: {confidence}")

                feature_data[feature]["negative_count"] += 1
            else:
                score = 3
                feature_data[feature]["neutral_count"] += 1

            feature_data[feature]["ratings"].append(score)
            print(f"Calculated score: {score}--------------------*****------------")

        return feature_data

