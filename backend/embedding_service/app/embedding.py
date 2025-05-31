"""Module for generating embeddings for menu items.

Defines EmbeddingService, which can be injected for testability and modularity.
"""

import asyncio
from typing import List, Dict, Any, Optional
from functools import lru_cache

import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import logger, settings

# Configure genai
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


class EmbeddingService:
    """Service for generating embeddings using Google AI models."""

    def __init__(self, api_key: str, model_name: str):
        """Initialize the embedding service.

        Args:
            api_key: API key for the embedding model
            model_name: Name of the embedding model
        """
        self.model = None

        if api_key:
            try:
                self.model = GoogleGenerativeAIEmbeddings(
                    model=model_name,
                    google_api_key=api_key,
                    credentials=None
                )
                logger.info("Embedding model initialized: %s", model_name)
            except Exception as e:
                logger.error("Error initializing embedding model: %s", str(e))

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a text string.

        Args:
            text: Input text to generate embedding for

        Returns:
            List of floats representing the embedding vector, or None if error
        """
        if not self.model:
            logger.warning("Embedding model not initialized")
            return None

        try:
            return await asyncio.to_thread(self.model.embed_query, text)
        except Exception as e:
            logger.error("Error generating embedding: %s", str(e))
            return None

    async def generate_menu_item_embedding(self, item: Dict[str, Any]) -> Optional[List[float]]:
        """Generate embedding for a menu item by combining its text fields.

        Args:
            item: Menu item dictionary with name and possibly size, description, etc.

        Returns:
            List of floats representing the embedding vector
        """
        try:
            item_text = item.get("name", "")

            if "size" in item and item["size"]:
                item_text += f" {item['size']}"

            if "description" in item and item["description"]:
                item_text += f". {item['description']}"

            if "category" in item and item["category"]:
                item_text += f". Category: {item['category']}"

            return await self.generate_embedding(item_text)

        except Exception as e:
            logger.error("Error generating menu item embedding: %s", str(e))
            return None


@lru_cache(maxsize=1)
def get_embedding_service() -> Optional[EmbeddingService]:
    """Get embedding service singleton instance.

    Returns:
        Embedding service instance or None if initialization fails
    """
    if not settings.gemini_api_key:
        logger.error("Missing Gemini API key")
        return None

    try:
        return EmbeddingService(
            api_key=settings.gemini_api_key,
            model_name=settings.embedding_model
        )
    except Exception as e:
        logger.error("Failed to initialize embedding service: %s", str(e))
        return None


# Initialize embedding service
embedding_service = get_embedding_service()


async def generate_menu_item_embedding(item: Dict[str, Any]) -> List[float]:
    """Generate embedding for a menu item.

    Args:
        item: Menu item dictionary

    Returns:
        List of floats representing the embedding vector
    """
    if not embedding_service:
        logger.warning("Embedding service not available")
        return []

    embedding = await embedding_service.generate_menu_item_embedding(item)
    return embedding or []
