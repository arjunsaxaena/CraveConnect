from sqlalchemy.orm import Session
from uuid import UUID
from app.repositories.repository import MenuItemEmbeddingRepository
from app.models.menu_item_embedding import MenuItemEmbedding, validate_menu_item_embedding
from app.core.errors import BadRequestError
from app.core.config import settings
import google.generativeai as genai
import logging
import numpy as np
from app.schemas.menu_item_embedding import MenuItemEmbeddingCreate

if hasattr(settings, 'GEMINI_API_KEY'):
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    raise RuntimeError("GEMINI_API_KEY not found in settings")

def get_menu_item_text(menu_item) -> str:
    parts = [menu_item.name]
    if menu_item.description:
        parts.append(menu_item.description)
    if menu_item.options:
        for option in menu_item.options:
            parts.append(f"Option: {option.get('name', '')} - {option.get('description', '')} - {option.get('price', '')}")
    if menu_item.tags:
        parts.append(f"Tags: {', '.join(menu_item.tags)}")
    if menu_item.allergens:
        parts.append(f"Allergens: {', '.join(menu_item.allergens)}")
    return " | ".join(parts)

def create_menu_item_embedding(db: Session, menu_item_id: UUID, menu_item) -> None:
    try:
        text = get_menu_item_text(menu_item)
        response = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )
        embedding = response['embedding'] if isinstance(response, dict) and 'embedding' in response else response

        if not isinstance(embedding, list) or len(embedding) != 768:
            raise BadRequestError(f"Embedding returned is not 768-dim: got {len(embedding) if isinstance(embedding, list) else 'invalid'}")
        embedding_obj = MenuItemEmbeddingCreate(
            menu_item_id=menu_item_id,
            embedding=embedding,
            meta={}
        )
        repo = MenuItemEmbeddingRepository()
        repo.create(db, obj_in=embedding_obj)
    except Exception as e:
        logging.error(f"Failed to create embedding for menu item {menu_item_id}: {e}")
        raise BadRequestError(f"Failed to create embedding: {e}") 