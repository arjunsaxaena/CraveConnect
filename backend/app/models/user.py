from sqlalchemy import Column, String, Enum, DateTime, JSON, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from .enums import AuthProvider
import uuid
from app.db.tables import Tables


class User(Base):
    __tablename__ = Tables.USERS
    __table_args__ = (UniqueConstraint('email', name='uq_user_email'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    provider = Column(Enum(AuthProvider, name='auth_provider'), nullable=False)
    address = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})
