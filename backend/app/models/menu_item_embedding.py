from sqlalchemy import Column, ForeignKey, DateTime, JSON, func
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.db.tables import Tables
from app.core.errors import errors


class MenuItemEmbedding(Base):
    __tablename__ = Tables.MENU_ITEM_EMBEDDINGS

    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_menu_item_embedding(menu_item_embedding: MenuItemEmbedding):
    if menu_item_embedding.menu_item_id is None:
        raise errors.BadRequestError("Menu item ID must be provided")

    if menu_item_embedding.embedding is None:
        raise errors.BadRequestError("Embedding must be provided")

    return menu_item_embedding
