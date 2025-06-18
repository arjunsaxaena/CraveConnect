from pydantic import BaseModel, Field
from typing import Any, List, Optional

class SuccessResponse(BaseModel):
    message: str = Field(..., example="Operation successful")
    meta: Optional[dict] = Field(None, example={"info": "Additional metadata"})

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Resource not found")
    code: Optional[int] = Field(None, example=404)
    errors: Optional[Any] = Field(None, example={"field": "error message"})

class DataResponse(BaseModel):
    data: Any
    message: str = Field(..., example="Data fetched successfully")
    meta: Optional[dict] = None

class ListResponse(BaseModel):
    data: List[Any]
    message: str = Field(..., example="List fetched successfully")
    meta: Optional[dict] = Field(None, example={"total": 100, "page": 1, "size": 10}) 