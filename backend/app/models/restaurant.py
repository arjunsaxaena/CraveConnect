from sqlalchemy import Column, String, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.core.errors import errors
from app.db.tables import Tables
from sqlalchemy.orm import relationship

class Restaurant(Base):
    __tablename__ = Tables.RESTAURANTS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, default=dict)

    addresses = relationship('Address', back_populates='restaurant', cascade='all, delete-orphan')


def validate_restaurant(restaurant: Restaurant):
    if restaurant.name is None or restaurant.name == "":
        raise errors.BadRequestError("Name must be provided")

    if restaurant.owner_id is None:
        raise errors.BadRequestError("Owner ID must be provided")

    return restaurant
