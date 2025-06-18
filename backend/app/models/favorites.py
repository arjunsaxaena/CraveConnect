from sqlalchemy import Column, ForeignKey, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class Favorites(Base):
    __tablename__ = Tables.FAVORITES

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True, nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_favorites(favorites: Favorites):
    if favorites.user_id is None:
        raise errors.BadRequestError("User ID must be provided")

    if favorites.menu_item_id is None:
        raise errors.BadRequestError("Menu item ID must be provided")

    return favorites
