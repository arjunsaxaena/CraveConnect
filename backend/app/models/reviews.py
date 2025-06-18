from sqlalchemy import Column, String, DateTime, Integer, JSON, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class Review(Base):
    __tablename__ = Tables.REVIEWS
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_review(review: Review):
    if review.user_id is None:
        raise errors.BadRequestError("User ID must be provided")

    if review.restaurant_id is None:
        raise errors.BadRequestError("Restaurant ID must be provided")

    if review.rating is None or review.rating < 1 or review.rating > 5:
        raise errors.BadRequestError("Rating must be between 1 and 5")

    return review
