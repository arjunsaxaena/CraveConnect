from sqlalchemy import Column, ForeignKey, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class OrderAssignments(Base):
    __tablename__ = Tables.ORDER_ASSIGNMENTS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    delivery_person_id = Column(UUID(as_uuid=True), ForeignKey('delivery_persons.id'), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_order_assignments(order_assignments: OrderAssignments):
    if order_assignments.order_id is None:
        raise errors.BadRequestError("Order ID must be provided")

    if order_assignments.delivery_person_id is None:
        raise errors.BadRequestError("Delivery person ID must be provided")

    return order_assignments
