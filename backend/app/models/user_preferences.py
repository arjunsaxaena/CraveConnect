from sqlalchemy import Column, ForeignKey, DateTime, JSON, func, Enum, Array, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from .enums import SpiceTolerance


class UserPreferences(Base):
    __tablename__ = 'user_preferences'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True, nullable=False)
    preferred_cuisines = Column(Array(String), nullable=False)
    dietary_restrictions = Column(Array(String), nullable=False)
    spice_tolerance = Column(Enum(SpiceTolerance), nullable=False)
    allergies = Column(Array(String), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True)
