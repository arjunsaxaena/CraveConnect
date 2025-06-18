from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables


class MenuItemAddons(Base):
    __tablename__ = Tables.MENU_ITEM_ADDONS

    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True, nullable=False)
    addon_id = Column(UUID(as_uuid=True), ForeignKey('addons.id'), primary_key=True, nullable=False)
