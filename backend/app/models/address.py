from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Double, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base
from app.db.tables import Tables

class Address(Base):
    __tablename__ = Tables.ADDRESSES

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.id'), nullable=True)
    alias = Column(String, nullable=True)
    street = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(Integer, nullable=True)
    landmark = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)
    latitude = Column(Double, nullable=True)
    longitude = Column(Double, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, default=dict)

    user = relationship('User', back_populates='addresses', foreign_keys=[user_id])
    restaurant = relationship('Restaurant', back_populates='addresses', foreign_keys=[restaurant_id]) 