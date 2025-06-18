from sqlalchemy import Column, String, DateTime, Array, JSON, func, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(Array(String), nullable=True)
    allergens = Column(Array(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})
