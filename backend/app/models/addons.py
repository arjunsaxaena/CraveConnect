from sqlalchemy import Column, String, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.db.tables import Tables
from app.core.errors import errors
import uuid


class Addons(Base):
    __tablename__ = Tables.ADDONS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    options = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_addons(addons: Addons):
    if addons.name is None or addons.name == "":
        raise errors.BadRequestError("Name must be provided")

    if not addons.options or len(addons.options) == 0:
        raise errors.BadRequestError("At least one option must be provided")

    for option in addons.options:
        if option.get('price', 0) <= 0:
            raise errors.BadRequestError("Each option must have a price greater than 0")

    return addons
