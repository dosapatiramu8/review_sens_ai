from functools import lru_cache

from langchain_groq import ChatGroq


@lru_cache(maxsize=1)  # Cache only one instance (singleton behavior)
def get_llm(groq_token: str):
    """
    Get a singleton LLM instance for the given Groq token.

    Args:
        groq_token (str): The Groq API token.

    Returns:
        ChatGroq: A singleton instance of the ChatGroq LLM.
    """
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=1,
        groq_api_key=groq_token  # Pass the Groq token here
    )
