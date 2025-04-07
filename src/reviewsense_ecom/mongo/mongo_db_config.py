import urllib.parse
from datetime import datetime, timezone

from pymongo import MongoClient

from src.reviewsense_ecom.model.FeatureSentiment import FeatureSentiment
from src.reviewsense_ecom.model.Product import Product
from src.reviewsense_ecom.model.ProductReview import ProductReview


# def get_db_connection(collection_name: str):   #LOCAL DB
#     client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB connection
#     db = client["productRater"]  # Change to your database name
#     return db[collection_name]  # db["productFeatureRater"]  # Change to your collection name


def get_db_connection(collection_name: str):  # get_db_cloud_connection
    password = "nisum@123"
    escaped_password = urllib.parse.quote_plus(password)
    client = MongoClient(
        f"mongodb+srv://genai:{escaped_password}@productrater.hpbsn.mongodb.net/?retryWrites=true&w=majority&appName=productRater")  # Update with your MongoDB connection
    db = client["productRater"]  # Change to your database name
    return db[collection_name]


def insert_product(product_id):  # Use this method to insert if null
    collection = get_db_connection("productFeatureRater")
    new_product = {
        "product_id": product_id,
        "category": "Electronics",  # Default category (can be updated later)
        "features": {},  # Empty features dictionary, to be filled later
        "ratings_distribution": {str(i): 0 for i in range(1, 6)},  # Rating count (1-5 stars)
        "overall_rating": 0.0,  # Default overall rating
        "total_reviews": 0,  # No reviews initially
        "created_at": datetime.now(timezone.utc),  # issue could be
        "updated_at": datetime.now(timezone.utc),
        # "review_ratings": {},  # Placeholder for review-specific ratings
        # "ratings_summary": {}  # Placeholder for summarized rating data
    }
    collection.insert_one(new_product)
    print("Product inserted successfully.")


def update_product(product_id, update_data):
    collection = get_db_connection("productFeatureRater")

    # Set the updated timestamp
    update_data["updated_at"] = datetime.now(timezone.utc)

    # Ensure required fields are included in the update data if missing
    update_data.setdefault("review_ratings", {})
    update_data.setdefault("ratings_summary", {})

    print(f"Updated Data with Timestamp: {update_data}")

    try:
        result = collection.update_one(
            {"product_id": product_id},
            {"$set": update_data},
            upsert=True  # 🔥 This will create a new product if none exists
        )
    except Exception as e:
        print(f"Error updating product: {e}")
        return None

    if result.matched_count > 0:
        print("Product updated successfully.")
    elif result.upserted_id:
        print(f"New product created with ID: {result.upserted_id}")

    return update_data


def get_product_by_id(product_id):
    collection = get_db_connection("productFeatureRater")
    product_data = collection.find_one({"product_id": product_id})

    if product_data:
        product = Product.from_dict(product_data)
        print("Product found:", product)
        return product
    else:
        print("No product found with the given ID.")
        return None


# add New Reviews to MongoDB
def add_review(input_data, reviews_by_feature):
    collection = get_db_connection("productReviews")
    # now we need to set the feature sentance according to sentiment in the feature list
    new_review = ProductReview(
        product_id=input_data.product_id,
        review=input_data.new_review,
        rating=input_data.new_rating,
        # feature=reviews_by_feature.feature
    )
    collection.insert_one(new_review.__dict__)


# adding New Reviews to productReview Collection
def add_review_features(input_data, reviews_by_feature):
    collection = get_db_connection("productReviews")

    # Create a dictionary to store features with their corresponding sentiments
    feature_sentiments = {}

    for review in reviews_by_feature:
        feature = review["feature"]
        sentiment = review["sentiment"]
        sentence = review["sentence"]

        # Initialize the feature if not already present
        if feature not in feature_sentiments:
            feature_sentiments[feature] = FeatureSentiment()

        # Append sentences to the correct sentiment list
        if sentiment == "positive":
            feature_sentiments[feature].positive.append(sentence)
        elif sentiment == "negative":
            feature_sentiments[feature].negative.append(sentence)

    # Convert FeatureSentiment objects to dictionaries before storing
    features_list = [{key: value.__dict__} for key, value in feature_sentiments.items()]

    # Create the ProductReview object
    new_review = ProductReview(
        product_id=input_data.product_id,
        review=input_data.new_review,
        rating=input_data.new_rating,
        features=features_list
    )

    # Convert the ProductReview instance to a dictionary before inserting
    inserted_result = collection.insert_one(new_review.__dict__)

    if inserted_result.inserted_id:
        print(f"Review successfully added with ID: {inserted_result.inserted_id}")

    # Return the newly inserted review object
    return new_review.__dict__


def product_feature(product_id):
    collection = get_db_connection("productFeatures")
    product = collection.find_one({"product_id": product_id}, {"_id": 0, "feature": 1})

    if product and "feature" in product:
        return product["feature"]
    return []
