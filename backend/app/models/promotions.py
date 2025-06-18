from sqlalchemy import Column, String, DateTime, JSON, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables


class Promotion(Base):
    __tablename__ = Tables.PROMOTIONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    discount_percent = Column(Numeric(5, 2), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})