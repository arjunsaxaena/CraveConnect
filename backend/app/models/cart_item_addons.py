from sqlalchemy import Column, DateTime, JSON, func, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class CartItemAddon(Base):
    __tablename__ = Tables.CART_ITEM_ADDONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cart_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    addon_id = Column(UUID(as_uuid=True), ForeignKey("addons.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    addon_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    meta = Column(JSON, nullable=True, default={})

    # Relationships
    cart_item = relationship("CartItem", back_populates="addons")


def validate_cart_item_addon(cart_item_addon: CartItemAddon):
    if cart_item_addon.cart_item_id is None:
        raise errors.BadRequestError("Cart item ID must be provided")
    if cart_item_addon.addon_id is None:
        raise errors.BadRequestError("Addon ID must be provided")
    if cart_item_addon.quantity is None or cart_item_addon.quantity <= 0:
        raise errors.BadRequestError("Quantity must be greater than 0")
    if cart_item_addon.addon_price is None or cart_item_addon.addon_price < 0:
        raise errors.BadRequestError("Addon price must be greater than or equal to 0")
    return cart_item_addon
