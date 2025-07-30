from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    func,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class Cart(Base):
    __tablename__ = Tables.CARTS
    __table_args__ = (UniqueConstraint("user_id", "restaurant_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    restaurant_id = Column(
        UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    meta = Column(JSON, nullable=True, default={})

    # Relationships
    items = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="carts")
    restaurant = relationship("Restaurant", back_populates="carts")


def validate_cart(cart: Cart):
    if cart.user_id is None:
        raise errors.BadRequestError("User ID must be provided")
    if cart.restaurant_id is None:
        raise errors.BadRequestError("Restaurant ID must be provided")
    return cart
