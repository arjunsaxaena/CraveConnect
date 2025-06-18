from sqlalchemy import Column, String, Enum, DateTime, JSON, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from .enums import FileTypes
from app.db.tables import Tables
from app.core.errors import errors


class File(Base):
    __tablename__ = Tables.FILES

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_url = Column(String, nullable=False)
    file_type = Column(Enum(FileTypes, name='file_type'), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, nullable=True, default={})


def validate_file(file: File):
    if file.file_url is None or file.file_url == "":
        raise errors.BadRequestError("File URL must be provided")

    if file.file_type is None:
        raise errors.BadRequestError("File type must be provided")

    if file.uploaded_by is None:
        raise errors.BadRequestError("Uploaded by must be provided")

    return file
