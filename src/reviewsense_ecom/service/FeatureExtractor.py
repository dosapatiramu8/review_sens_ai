from typing import List, Dict

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from src.reviewsense_ecom.llm.llm import get_llm

# Load environment variables from .env file
load_dotenv()


class FeatureReview(BaseModel):
    feature: str
    sentence: str
    sentiment: str
    confidence: str


class FeatureReviews(BaseModel):
    feature_reviews: List[FeatureReview]  # Each review will include a sentence and sentiment


class FeatureExtractor:
    def __init__(self):
        self.llm = get_llm("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")
        self.parser = self._create_reviews_parser()
        self.prompt = self._create_extraction_prompt()

    def _create_reviews_parser(self) -> JsonOutputParser:
        """Create JSON parser for feature-specific reviews extraction"""
        return JsonOutputParser(pydantic_object=FeatureReviews)

    def _create_extraction_prompt(self) -> ChatPromptTemplate:
        """Create prompt for extracting feature-specific reviews with enhanced rules and sentiment analysis."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract sentences about the given feature from the list of reviews.

                Rules:
                - Extract only parts discussing the specific feature.
                - Remove unrelated parts connected by 'and' or 'but'.
                - Keep original wording and capitalization.
                - If there are multiple sentences related a particular feature in a review, merge them into one.
                - If there is only one review, apply the same rules to extract sentences about the feature.

                Return only the parts discussing the specific feature and perform sentiment analysis for each extracted sentence in this JSON format:
                {{
                    "feature_reviews": [
                        {{ 
                            "feature" : "feature 1",
                            "sentence": "relevant sentence 1",
                            "sentiment": "positive/negative/neutral",
                            "confidence": "confidence score between 0 and 1"
                        }},
                        {{
                            "feature" : "feature 2",
                            "sentence": "relevant sentence 2",
                            "sentiment": "positive/negative/neutral",
                            "confidence": "confidence score between 0 and 1"
                        }}
                    ]
                }}"""),
            ("user", "{inputFeatures}"),
            ("user", "{inputReview}"),
        ])
        return prompt

    def extract_feature_reviews(self, review: str, features: List[str]) -> List[Dict[str, str]]:
        """
        Extract feature-specific sentences from reviews with sentiment analysis.

        Args:
            review (str): Review text.
            features (List[str]): List of features to extract.

        Returns:
            List[Dict[str, str]]: Feature-specific sentences with sentiment analysis.
        """
        try:
            chain = self.prompt | self.llm | self.parser
            result = chain.invoke({"inputFeatures": f"features : {features}",
                                   "inputReview": review})
            return result['feature_reviews']
        except Exception as e:
            print(f"Error extracting feature reviews: {e}")
            return []
