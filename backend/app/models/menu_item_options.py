from sqlalchemy import Column, String, DateTime, JSON, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class MenuItemOptions(Base):
    __tablename__ = Tables.MENU_ITEM_OPTIONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_menu_item_options(menu_item_options: MenuItemOptions):
    if menu_item_options.menu_item_id is None:
        raise errors.BadRequestError("Menu item ID must be provided")

    if menu_item_options.name is None or menu_item_options.name == "":
        raise errors.BadRequestError("Name must be provided")

    if menu_item_options.price is None or menu_item_options.price <= 0:
        raise errors.BadRequestError("Price must be greater than 0")

    return menu_item_options
