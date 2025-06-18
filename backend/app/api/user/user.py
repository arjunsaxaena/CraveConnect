from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import UserRepository
from app.models.user import User, validate_user
from app.models.filters import GetUserFilters
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserListResponse, UserSingleResponse

router = APIRouter(prefix="/users", tags=["users"])
user_repo = UserRepository()

@router.get("/", response_model=UserListResponse, responses={404: {"model": ErrorResponse}})
def list_users(filters: GetUserFilters = Depends(), db: Session = Depends(get_db)):
    users = user_repo.get(db, filters=filters)
    if not users:
        raise NotFoundError("No users found")
    return UserListResponse(data=users)

@router.post("/", response_model=UserSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        user_obj = User(**user_in.dict())
        validate_user(user_obj)
        created = user_repo.create(db, obj_in=user_in)
        return UserSingleResponse(data=created, message="User created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=UserSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_user(user_id: str = Query(...), user_in: UserUpdate = None, db: Session = Depends(get_db)):
    user = user_repo.get(db, id=user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")
    try:
        updated = user_repo.update(db, db_obj=user, obj_in=user_in)
        return UserSingleResponse(data=updated, message="User updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{user_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = user_repo.get(db, id=user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")
    user_repo.delete(db, id=user_id)
    return SuccessResponse(message=f"User {user_id} deleted successfully")
