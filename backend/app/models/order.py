from sqlalchemy import Column, DateTime, JSON, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class Order(Base):
    __tablename__ = Tables.ORDERS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.id'), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_order(order: Order):
    if order.user_id is None:
        raise errors.BadRequestError("User ID must be provided")

    if order.restaurant_id is None:
        raise errors.BadRequestError("Restaurant ID must be provided")

    if order.total_price is None or order.total_price <= 0:
        raise errors.BadRequestError("Total price must be greater than 0")

    return order
