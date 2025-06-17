from sqlalchemy import Column, String, Enum, DateTime, JSON, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from .enums import VehicleType
import uuid


class DeliveryPerson(Base):
    __tablename__ = 'delivery_persons'
    __table_args__ = (UniqueConstraint('phone_number', name='uq_delivery_person_phone_number'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    vehicle_details = Column(String, nullable=True)
    vehicle_type = Column(Enum(VehicleType, name='vehicle_type'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True)
