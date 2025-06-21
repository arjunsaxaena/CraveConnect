from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from fastapi import Form
import json

class FileCreate(BaseModel):
    file_url: str
    file_type: str
    uploaded_by: UUID
    meta: Optional[dict] = None

class FileCreateForm:
    def __init__(
        self,
        file_type: str = Form(...),
        uploaded_by: UUID = Form(...),
        meta: Optional[str] = Form(None)
    ):
        self.file_type = file_type
        self.uploaded_by = uploaded_by
        self.meta = json.loads(meta) if meta else None

class FileUpdate(BaseModel):
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    meta: Optional[dict] = None

class FileOut(BaseModel):
    id: UUID
    file_url: str
    file_type: str
    uploaded_by: UUID
    meta: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }

class FileListResponse(BaseModel):
    data: List[FileOut]
    message: str = "Files fetched successfully"

class FileSingleResponse(BaseModel):
    data: FileOut
    message: str = "File fetched successfully"
