from sqlalchemy import Column, ForeignKey, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.db.tables import Tables
from app.core.errors import errors
import uuid


class MenuItemAddons(Base):
    __tablename__ = Tables.MENU_ITEM_ADDONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), nullable=False)
    addon_id = Column(UUID(as_uuid=True), ForeignKey('addons.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_menu_item_addons(menu_item_addons: MenuItemAddons):
    if menu_item_addons.menu_item_id is None:
        raise errors.BadRequestError("Menu item ID must be provided")

    if menu_item_addons.addon_id is None:
        raise errors.BadRequestError("Addon ID must be provided")
    
    return menu_item_addons
