from sqlalchemy import Column, String, DateTime, JSON, func,  ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables


class Restaurant(Base):
    __tablename__ = Tables.RESTAURANTS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(JSON, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})
