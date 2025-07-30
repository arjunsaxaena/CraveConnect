from sqlalchemy import Column, DateTime, JSON, func, ForeignKey, Numeric, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from .enums import PaymentStatus
from app.db.tables import Tables
from app.core.errors import errors


class PaymentHistory(Base):
    __tablename__ = Tables.PAYMENT_HISTORY

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    items = Column(ARRAY(String), nullable=False)
    prices = Column(ARRAY(Numeric(10, 2)), nullable=False)
    razorpay_payment_id = Column(String, nullable=True)
    razorpay_order_id = Column(String, nullable=True)
    razorpay_signature = Column(String, nullable=True)
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())
    purchase_status = Column(String, default="COMPLETED")
    payment_method = Column(String, nullable=True)
    totalAmount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String, default="SUCCESSFUL")
    notes = Column(JSON, nullable=True)
    raw_payload = Column(JSON, nullable=True)
    payment_timestamp = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


def validate_payment(payment: PaymentHistory):
    if payment.user_id is None:
        raise errors.BadRequestError("User ID must be provided")
    if payment.totalAmount is None or payment.totalAmount <= 0:
        raise errors.BadRequestError("Total amount must be greater than 0")
    if payment.payment_status is None:
        raise errors.BadRequestError("Payment status must be provided")
    if not payment.items or len(payment.items) == 0:
        raise errors.BadRequestError("Items must be provided")
    if not payment.prices or len(payment.prices) == 0:
        raise errors.BadRequestError("Prices must be provided")
    if len(payment.items) != len(payment.prices):
        raise errors.BadRequestError("Items and prices count must match")
    return payment
