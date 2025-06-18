from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import UserPreferencesRepository
from app.models.user_preferences import UserPreferences, validate_user_preferences
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.user_preferences import (
    UserPreferencesCreate, UserPreferencesUpdate, UserPreferencesListResponse, UserPreferencesSingleResponse
)

router = APIRouter(prefix="/user-preferences", tags=["user-preferences"])
user_preferences_repo = UserPreferencesRepository()

@router.get("/", response_model=UserPreferencesListResponse, responses={404: {"model": ErrorResponse}})
def list_user_preferences(db: Session = Depends(get_db)):
    preferences = user_preferences_repo.get(db)
    if not preferences:
        raise NotFoundError("No user preferences found")
    return UserPreferencesListResponse(data=preferences)

@router.post("/", response_model=UserPreferencesSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_user_preferences(preferences_in: UserPreferencesCreate, db: Session = Depends(get_db)):
    try:
        preferences_obj = UserPreferences(**preferences_in.dict())
        validate_user_preferences(preferences_obj)
        created = user_preferences_repo.create(db, obj_in=preferences_in)
        return UserPreferencesSingleResponse(data=created, message="User preferences created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=UserPreferencesSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_user_preferences(user_id: str = Query(...), preferences_in: UserPreferencesUpdate = None, db: Session = Depends(get_db)):
    preferences = user_preferences_repo.get(db, filters={"user_id": user_id})
    if not preferences:
        raise NotFoundError(f"User preferences for user {user_id} not found")
    try:
        updated = user_preferences_repo.update(db, db_obj=preferences[0], obj_in=preferences_in)
        return UserPreferencesSingleResponse(data=updated, message="User preferences updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{user_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_user_preferences(user_id: str, db: Session = Depends(get_db)):
    preferences = user_preferences_repo.get(db, filters={"user_id": user_id})
    if not preferences:
        raise NotFoundError(f"User preferences for user {user_id} not found")
    user_preferences_repo.delete(db, id={"user_id": user_id})
    return SuccessResponse(message=f"User preferences for user {user_id} deleted successfully")
