from sqlalchemy import Column, String, DateTime, JSON, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from app.db.tables import Tables
from app.core.errors import errors


class Queries(Base):
    __tablename__ = Tables.QUERIES

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    query_text = Column(String, nullable=False)
    context = Column(JSON, nullable=True)
    feedback = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_queries(queries: Queries):
    if queries.user_id is None:
        raise errors.BadRequestError("User ID must be provided")

    if queries.query_text is None or queries.query_text == "":
        raise errors.BadRequestError("Query text must be provided")

    return queries
