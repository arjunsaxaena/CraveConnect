from sqlalchemy import Column, Enum, DateTime, JSON, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from .enums import PaymentStatus
from app.db.tables import Tables
from app.core.errors import errors


class Payment(Base):
    __tablename__ = Tables.PAYMENTS
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus, name='payment_status'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_payment(payment: Payment):
    if payment.order_id is None:
        raise errors.BadRequestError("Order ID must be provided")

    if payment.amount is None or payment.amount <= 0:
        raise errors.BadRequestError("Amount must be greater than 0")

    if payment.status is None:
        raise errors.BadRequestError("Status must be provided")

    return payment
