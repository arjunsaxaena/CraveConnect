from sqlalchemy import Column, ForeignKey, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid


class Favorites(Base):
    __tablename__ = 'favorites'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True, nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})
