from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Dict

class QueryCreate(BaseModel):
    user_id: UUID
    query_text: str
    context: Optional[Dict] = None
    feedback: Optional[str] = None
    meta: Optional[dict] = None

class QueryOut(BaseModel):
    id: UUID
    user_id: UUID
    query_text: str
    context: Optional[Dict] = None
    feedback: Optional[str] = None
    meta: Optional[dict] = None 