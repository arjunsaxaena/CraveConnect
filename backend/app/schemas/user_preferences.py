from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from enum import Enum
from datetime import datetime


class SpiceTolerance(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class UserPreferencesCreate(BaseModel):
    user_id: UUID
    preferred_cuisines: List[str]
    dietary_restrictions: List[str]
    spice_tolerance: SpiceTolerance
    allergies: List[str]
    meta: Optional[dict] = None


class UserPreferencesUpdate(BaseModel):
    preferred_cuisines: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    spice_tolerance: Optional[SpiceTolerance] = None
    allergies: Optional[List[str]] = None
    meta: Optional[dict] = None


class UserPreferencesOut(BaseModel):
    user_id: UUID
    preferred_cuisines: List[str]
    dietary_restrictions: List[str]
    spice_tolerance: SpiceTolerance
    allergies: List[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    meta: Optional[dict]

    model_config = {"from_attributes": True}


class UserPreferencesListResponse(BaseModel):
    data: List[UserPreferencesOut]
    message: str = "User preferences fetched successfully"


class UserPreferencesSingleResponse(BaseModel):
    data: UserPreferencesOut
    message: str = "User preferences fetched successfully"
