from sqlalchemy import Column, ForeignKey, DateTime, JSON, func, Float, Vector
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables


class MenuItemEmbedding(Base):
    __tablename__ = Tables.MENU_ITEM_EMBEDDINGS

    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})
