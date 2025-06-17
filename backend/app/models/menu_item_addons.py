from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid


class MenuItemAddons(Base):
    __tablename__ = 'menu_item_addons'

    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True, nullable=False)
    addon_id = Column(UUID(as_uuid=True), ForeignKey('addons.id'), primary_key=True, nullable=False)
