from sqlalchemy import Column, String, Enum, DateTime, JSON, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from .enums import AuthProvider
import uuid
from app.db.tables import Tables
from app.core.errors import errors
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = Tables.USERS
    __table_args__ = (UniqueConstraint('email', name='uq_user_email'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    provider = Column(Enum(AuthProvider, name='auth_provider'), nullable=False)
    session_location = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})

    addresses = relationship('Address', back_populates='user', cascade='all, delete-orphan')

def validate_user(user: User):
    if user.name is None or user.name == "":
        raise errors.BadRequestError("Name must be provided")

    if user.email is None or user.email == "":
        raise errors.BadRequestError("Email must be provided")

    if user.provider is None:
        raise errors.BadRequestError("Provider must be provided")

    return user
