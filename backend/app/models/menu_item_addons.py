from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.db.tables import Tables
from app.core.errors import errors


class MenuItemAddons(Base):
    __tablename__ = Tables.MENU_ITEM_ADDONS

    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True, nullable=False)
    addon_id = Column(UUID(as_uuid=True), ForeignKey('addons.id'), primary_key=True, nullable=False)


def validate_menu_item_addons(menu_item_addons: MenuItemAddons):
    if menu_item_addons.menu_item_id is None:
        raise errors.BadRequestError("Menu item ID must be provided")

    if menu_item_addons.addon_id is None:
        raise errors.BadRequestError("Addon ID must be provided")
    
    return menu_item_addons
