from sqlalchemy import Column, ForeignKey, DateTime, JSON, func, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class Recommendation(Base):
    __tablename__ = Tables.RECOMMENDATIONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey('queries.id'), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), nullable=False)
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_recommendation(recommendation: Recommendation):
    if recommendation.query_id is None:
        raise errors.BadRequestError("Query ID must be provided")

    if recommendation.menu_item_id is None:
        raise errors.BadRequestError("Menu item ID must be provided")

    if recommendation.confidence_score is None or recommendation.confidence_score < 0:
        raise errors.BadRequestError("Confidence score must be greater than 0")

    return recommendation
