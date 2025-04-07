# src/reviewsense/core/database.py
from functools import lru_cache

from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


@lru_cache(maxsize=1)
def get_vector_store(
        collection_name: str = "feature_reviews",
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
):
    """
    Create a singleton vector store instance
    
    Args:
        collection_name (str): Database collection name
        embedding_model (str): Embedding model to use
    
    Returns:
        AstraDBVectorStore: Configured vector store instance
    """

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    # Create and return vector store
    return AstraDBVectorStore(
        collection_name=collection_name,
        embedding=embeddings,
        api_endpoint="https://19b6fcda-3fe8-4585-a5f5-6a464a382426-westus3.apps.astra.datastax.com",
        token="AstraCS:UaZmElcIDkRHzUmktguKwrnd:197d3e825510580f5f97cc749b00a94b685d54a5f1d4a755b75440fe2c29329b",
        namespace="default_keyspace",
    )
