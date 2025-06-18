from sqlalchemy import Column, ForeignKey, DateTime, JSON, func, Enum, Array, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from .enums import SpiceTolerance
from app.db.tables import Tables
from app.core.errors import errors


class UserPreferences(Base):
    __tablename__ = Tables.USER_PREFERENCES

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True, nullable=False)
    preferred_cuisines = Column(Array(String), nullable=False)
    dietary_restrictions = Column(Array(String), nullable=False)
    spice_tolerance = Column(Enum(SpiceTolerance), nullable=False)
    allergies = Column(Array(String), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_user_preferences(user_preferences: UserPreferences):
    if user_preferences.user_id is None:
        raise errors.BadRequestError("User ID must be provided")

    if user_preferences.preferred_cuisines is None:
        raise errors.BadRequestError("Preferred cuisines must be provided")

    if user_preferences.dietary_restrictions is None:
        raise errors.BadRequestError("Dietary restrictions must be provided")

    if user_preferences.spice_tolerance is None:
        raise errors.BadRequestError("Spice tolerance must be provided")

    if user_preferences.allergies is None:
        raise errors.BadRequestError("Allergies must be provided")

    return user_preferences
