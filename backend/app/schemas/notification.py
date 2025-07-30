from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str
    body: str
    seen: Optional[bool] = False
    meta: Optional[dict] = None


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    seen: Optional[bool] = None
    meta: Optional[dict] = None


class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    body: str
    seen: bool
    created_at: datetime
    updated_at: datetime
    meta: Optional[dict] = None

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    data: List[NotificationOut]
    message: str = "Notifications fetched successfully"


class NotificationSingleResponse(BaseModel):
    data: NotificationOut
    message: str = "Notification fetched successfully"
