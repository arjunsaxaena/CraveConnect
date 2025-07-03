import json
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.repositories.repository import MenuItemEmbeddingRepository, MenuItemRepository
import google.generativeai as genai
from app.core.config import settings

if hasattr(settings, 'GEMINI_API_KEY'):
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    raise RuntimeError("GEMINI_API_KEY not found in settings")

def resolve_query_gemini(db: Session, query_text: str, k: int = 5):

    response = genai.embed_content(
        model="models/embedding-001",
        content=query_text,
        task_type="RETRIEVAL_QUERY"
    )
    query_embedding = response['embedding']

    embedding_repo = MenuItemEmbeddingRepository()
    top_k_menu_item_ids = embedding_repo.get_top_k_similar(db, query_embedding, k=k)

    return [str(mid) for mid in top_k_menu_item_ids], {"confidence": 1.0, "method": "embedding_similarity"} 