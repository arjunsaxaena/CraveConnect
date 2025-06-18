from sqlalchemy import Column, ForeignKey, DateTime, JSON, func, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey('queries.id'), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), nullable=False)
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})
