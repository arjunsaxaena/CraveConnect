from sqlalchemy import (
    Column,
    DateTime,
    JSON,
    func,
    ForeignKey,
    Numeric,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class CartItem(Base):
    __tablename__ = Tables.CART_ITEMS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(
        UUID(as_uuid=True), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False
    )
    menu_item_id = Column(
        UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False
    )
    quantity = Column(Integer, nullable=False, default=1)
    base_price = Column(Numeric(10, 2), nullable=False)
    special_instructions = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    meta = Column(JSON, nullable=True, default={})

    # Relationships
    cart = relationship("Cart", back_populates="items")
    addons = relationship(
        "CartItemAddon", back_populates="cart_item", cascade="all, delete-orphan"
    )


def validate_cart_item(cart_item: CartItem):
    if cart_item.cart_id is None:
        raise errors.BadRequestError("Cart ID must be provided")
    if cart_item.menu_item_id is None:
        raise errors.BadRequestError("Menu item ID must be provided")
    if cart_item.quantity is None or cart_item.quantity <= 0:
        raise errors.BadRequestError("Quantity must be greater than 0")
    if cart_item.base_price is None or cart_item.base_price <= 0:
        raise errors.BadRequestError("Base price must be greater than 0")
    return cart_item
