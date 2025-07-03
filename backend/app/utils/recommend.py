from sqlalchemy.orm import Session
from app.repositories.repository import MenuItemEmbeddingRepository
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
    top_k = embedding_repo.get_top_k_similar(db, query_embedding, k=k)
    menu_item_ids = [str(mid) for mid, _ in top_k]
    confidences = {str(mid): float(conf) for mid, conf in top_k}

    return menu_item_ids, {"confidences": confidences, "method": "embedding_similarity"} 