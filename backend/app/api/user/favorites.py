from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import FavoritesRepository
from app.models.favorites import Favorites, validate_favorites
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.favorites import FavoritesCreate, FavoritesUpdate, FavoritesListResponse, FavoritesSingleResponse

router = APIRouter(prefix="/favorites", tags=["favorites"])
favorites_repo = FavoritesRepository()

@router.get("/", response_model=FavoritesListResponse, responses={404: {"model": ErrorResponse}})
def list_favorites(db: Session = Depends(get_db)):
    favorites = favorites_repo.get(db)
    if not favorites:
        raise NotFoundError("No favorites found")
    return FavoritesListResponse(data=favorites)

@router.post("/", response_model=FavoritesSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_favorite(favorite_in: FavoritesCreate, db: Session = Depends(get_db)):
    try:
        favorite_obj = Favorites(**favorite_in.dict())
        validate_favorites(favorite_obj)
        created = favorites_repo.create(db, obj_in=favorite_in)
        return FavoritesSingleResponse(data=created, message="Favorite created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=FavoritesSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_favorite(user_id: str = Query(...), menu_item_id: str = Query(...), favorite_in: FavoritesUpdate = None, db: Session = Depends(get_db)):
    favorite = favorites_repo.get(db, filters={"user_id": user_id, "menu_item_id": menu_item_id})
    if not favorite:
        raise NotFoundError(f"Favorite for user {user_id} and menu item {menu_item_id} not found")
    try:
        updated = favorites_repo.update(db, db_obj=favorite[0], obj_in=favorite_in)
        return FavoritesSingleResponse(data=updated, message="Favorite updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_favorite(user_id: str = Query(...), menu_item_id: str = Query(...), db: Session = Depends(get_db)):
    favorite = favorites_repo.get(db, filters={"user_id": user_id, "menu_item_id": menu_item_id})
    if not favorite:
        raise NotFoundError(f"Favorite for user {user_id} and menu item {menu_item_id} not found")
    favorites_repo.delete(db, id={"user_id": user_id, "menu_item_id": menu_item_id})
    return SuccessResponse(message=f"Favorite for user {user_id} and menu item {menu_item_id} deleted successfully")
