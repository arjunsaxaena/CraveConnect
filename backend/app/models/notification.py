from sqlalchemy import Column, String, DateTime, Boolean, JSON, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables


class Notification(Base):
    __tablename__ = Tables.NOTIFICATIONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    seen = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})
