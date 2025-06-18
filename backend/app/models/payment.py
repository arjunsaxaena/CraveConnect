from sqlalchemy import Column, Enum, DateTime, JSON, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from .enums import PaymentStatus
from app.db.tables import Tables


class Payment(Base):
    __tablename__ = Tables.PAYMENTS
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus, name='payment_status'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})