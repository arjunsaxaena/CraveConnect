from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import RestaurantRepository
from app.models.restaurant import Restaurant, validate_restaurant
from app.models.filters import GetRestaurantFilters
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.restaurant import RestaurantListResponse, RestaurantSingleResponse, RestaurantCreate, RestaurantUpdate
from app.repositories.repository import UserRepository

router = APIRouter(prefix="/restaurant", tags=["restaurant"])
restaurant_repo = RestaurantRepository()
user_repo = UserRepository()

@router.get("/", response_model=RestaurantListResponse, responses={404: {"model": ErrorResponse}})
def list_restaurants(filters: GetRestaurantFilters = Depends(), db: Session = Depends(get_db)):
    restaurants = restaurant_repo.get(db, filters=filters)
    if not restaurants:
        raise NotFoundError("No restaurants found")
    return RestaurantListResponse(data=restaurants)

@router.post("/", response_model=RestaurantSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_restaurant(restaurant_in: RestaurantCreate, db: Session = Depends(get_db)):
    try:
        restaurant_obj = Restaurant(**restaurant_in.dict())
        validate_restaurant(restaurant_obj)

        owner = user_repo.get(db, id=restaurant_in.owner_id)
        if not owner:
            raise NotFoundError(f"User {restaurant_in.owner_id} not found")

        created = restaurant_repo.create(db, obj_in=restaurant_in)
        return RestaurantSingleResponse(data=created, message="Restaurant created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=RestaurantSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_restaurant(restaurant_id: str = Query(...), restaurant_in: RestaurantUpdate = None, db: Session = Depends(get_db)):
    restaurant = restaurant_repo.get(db, id=restaurant_id)
    if not restaurant:
        raise NotFoundError(f"Restaurant {restaurant_id} not found")

    if restaurant_in.owner_id:
        owner = user_repo.get(db, id=restaurant_in.owner_id)
        if not owner:
            raise NotFoundError(f"User {restaurant_in.owner_id} not found")

    try:
        updated = restaurant_repo.update(db, db_obj=restaurant, obj_in=restaurant_in)
        return RestaurantSingleResponse(data=updated, message="Restaurant updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{restaurant_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    restaurant = restaurant_repo.get(db, id=restaurant_id)
    if not restaurant:
        raise NotFoundError(f"Restaurant {restaurant_id} not found")
    restaurant_repo.delete(db, id=restaurant_id)
    return SuccessResponse(message="Restaurant deleted successfully")

