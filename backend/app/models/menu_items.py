from sqlalchemy import Column, String, DateTime, ARRAY, JSON, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class MenuItem(Base):
    __tablename__ = Tables.MENU_ITEMS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    allergens = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_menu_item(menu_item: MenuItem):
    if menu_item.restaurant_id is None:
        raise errors.BadRequestError("Restaurant ID must be provided")

    if menu_item.name is None or menu_item.name == "":
        raise errors.BadRequestError("Name must be provided")

    return menu_item
