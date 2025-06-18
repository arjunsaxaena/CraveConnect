from sqlalchemy import Column, String, DateTime, JSON, func, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.db.tables import Tables
from app.core.errors import errors
import uuid


class Addons(Base):
    __tablename__ = Tables.ADDONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_addons(addons: Addons):
    if addons.name is None or addons.name == "":
        raise errors.BadRequestError("Name must be provided")

    if addons.price <= 0:
        raise errors.BadRequestError("Price must be greater than 0")

    return addons
