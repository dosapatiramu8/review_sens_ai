import logging

from fastapi import APIRouter, HTTPException

from src.reviewsense_ecom.model.PercentageResponseModel import PercentageResponseModel
from src.reviewsense_ecom.model.Product import Product
from src.reviewsense_ecom.model.ReviewResponseModel import ReviewResponseModel
from src.reviewsense_ecom.model.product_review_input import ProductReviewInput
from src.reviewsense_ecom.mongo.mongo_db_config import get_product_by_id, update_product, add_review_features, \
    insert_product, product_feature
from src.reviewsense_ecom.service.FeatureExtractor import FeatureExtractor
from src.reviewsense_ecom.service.FeatureUpdater import FeatureUpdater
from src.reviewsense_ecom.service.ReviewService import ReviewService

router = APIRouter()
review_service = ReviewService()
feature_extractor = FeatureExtractor()

logger = logging.getLogger(__name__)


@router.post("/calculate_ratings/", response_model=Product)
async def calculate_ratings(input_data: ProductReviewInput):  # Required
    """
    Endpoint to calculate feature-specific ratings

    Args:
        input_data (ProductReviewInput): Input data for review processing

    Returns:
        Updated Product object
    """
    logger.info(f"Received request: {input_data.dict()}")

    logger.info(f"InputData: {input_data.new_review}")

    product_data = get_product_by_id(input_data.product_id)

    # feature=get_db_connection("productFeature")
    # feature.fin by Product ID ()

    if product_data is None:
        logger.warning(f"Product with ID {input_data.product_id} not found. Creating a new product.")

        # Insert a new product into the database
        insert_product(input_data.product_id)

        # Re-fetch the product after insertion to ensure it exists
        product_data = get_product_by_id(input_data.product_id)

        if product_data is None:  # Double-check if insertion failed
            logger.error(f"Failed to insert product with ID {input_data.product_id}.")
            raise HTTPException(status_code=500, detail="Product creation failed")

    logger.info(f"Product Data: {product_data}")
    final_product = product_data
    if input_data.is_rating_evaluation_required:
        final_product = await update_product_data(input_data, product_data)

    logger.info(f"Final Return to Mongo: {final_product}")
    return final_product


@router.get("/fetch_percentage/", response_model=PercentageResponseModel)
async def fetch_percentage(product_id: str, features: str):  # NOT REQUIRED
    """
    Fetch reviews from MongoDB based on product_id and feature.
    """
    logger.info(f"Fetching reviews for product_id: {product_id}, feature: {features}")
    reviews = review_service.get_percentage_by_feature(product_id, features)
    if isinstance(reviews, dict):
        return reviews  # Return the dictionary directly

    return {"message": "No data found"}


@router.get("/fetch_full_reviews/", response_model=ReviewResponseModel)
async def fetch_review_by_feature(product_id: str, features: str):  # Required
    """
    Fetch reviews from MongoDB based on product_id and feature.
    """
    logger.info(f"Fetching reviews for product_id: {product_id}, feature: {features}")
    reviews = review_service.get_full_review_by_feature(product_id, features)
    if isinstance(reviews, dict):
        return reviews

    return {"reviews": reviews}


async def update_product_data(input_data, product_data):
    # ✅ Second Flow: Update Feature Ratings in Another Collection  FROM LLM
    features = product_feature(input_data.product_id)
    reviews_by_feature = feature_extractor.extract_feature_reviews(
        input_data.new_review, features)

    ratings = review_service.fetch_feature_ratings(reviews_by_feature)
    logger.info(f"Generated ratings: {ratings}")
    # ✅ First Flow: Add Review to a Separate Collection  TO REVIEWS
    new_review_data = add_review_features(input_data, reviews_by_feature)
    if new_review_data:
        logger.info(f"Successfully added review data: {new_review_data}")
    else:
        logger.warning("add_review() returned None. Review was not added.")
    updater = FeatureUpdater(product_data.to_dict())
    updated_product = updater.update_feature_ratings(ratings, input_data.new_rating)
    # Struck after this since this function is not creating new onject in feature
    logger.info(f"Updated Product Data: {updated_product}")
    # Save updated product back to the database
    updated_product_data = update_product(input_data.product_id, updated_product)
    if updated_product_data:
        final_product = Product.from_dict(updated_product_data)
        logger.info(f"Successfully updated product: {final_product}")
    else:
        logger.error("update_product() returned None. Update failed.")
        raise HTTPException(status_code=500, detail="Failed to update product")
    return final_product
