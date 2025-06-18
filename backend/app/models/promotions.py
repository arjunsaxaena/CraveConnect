from sqlalchemy import Column, String, DateTime, JSON, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class Promotion(Base):
    __tablename__ = Tables.PROMOTIONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    discount_percent = Column(Numeric(5, 2), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_promotion(promotion: Promotion):
    if promotion.restaurant_id is None:
        raise errors.BadRequestError("Restaurant ID must be provided")

    if promotion.title is None or promotion.title == "":
        raise errors.BadRequestError("Title must be provided")

    if promotion.discount_percent is None or promotion.discount_percent <= 0:
        raise errors.BadRequestError("Discount percent must be greater than 0")

    if promotion.valid_from is None:
        raise errors.BadRequestError("Valid from must be provided")

    if promotion.valid_to is None:
        raise errors.BadRequestError("Valid to must be provided")

    return promotion
