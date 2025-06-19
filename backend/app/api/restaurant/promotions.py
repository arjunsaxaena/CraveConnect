from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import PromotionRepository
from app.models.promotions import Promotion, validate_promotion
from app.models.filters import GetPromotionFilters
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.promotions import PromotionListResponse, PromotionSingleResponse, PromotionCreate, PromotionUpdate
from app.repositories.repository import RestaurantRepository

router = APIRouter(prefix="/promotions", tags=["promotions"])
promotion_repo = PromotionRepository()
restaurant_repo = RestaurantRepository()

@router.get("/", response_model=PromotionListResponse, responses={404: {"model": ErrorResponse}})
def list_promotions(filters: GetPromotionFilters = Depends(), db: Session = Depends(get_db)):
    promotions = promotion_repo.get(db, filters=filters)
    if not promotions:
        raise NotFoundError("No promotions found")
    return PromotionListResponse(data=promotions)

@router.post("/", response_model=PromotionSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_promotion(promotion_in: PromotionCreate, db: Session = Depends(get_db)):
    try:
        promotion_obj = Promotion(**promotion_in.dict())
        validate_promotion(promotion_obj)

        restaurant = restaurant_repo.get(db, id=promotion_in.restaurant_id)
        if not restaurant:
            raise NotFoundError(f"Restaurant {promotion_in.restaurant_id} not found")

        created = promotion_repo.create(db, obj_in=promotion_in)
        return PromotionSingleResponse(data=created, message="Promotion created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=PromotionSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_promotion(promotion_id: str = Query(...), promotion_in: PromotionUpdate = None, db: Session = Depends(get_db)):
    promotion = promotion_repo.get(db, id=promotion_id)
    if not promotion:
        raise NotFoundError(f"Promotion {promotion_id} not found")
    
    if promotion_in.restaurant_id:
        restaurant = restaurant_repo.get(db, id=promotion_in.restaurant_id)
        if not restaurant:
            raise NotFoundError(f"Restaurant {promotion_in.restaurant_id} not found")

    try:
        updated = promotion_repo.update(db, db_obj=promotion, obj_in=promotion_in)
        return PromotionSingleResponse(data=updated, message="Promotion updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{promotion_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_promotion(promotion_id: str, db: Session = Depends(get_db)):
    promotion = promotion_repo.get(db, id=promotion_id)
    if not promotion:
        raise NotFoundError(f"Promotion {promotion_id} not found")
    promotion_repo.delete(db, id=promotion_id)
    return SuccessResponse(message="Promotion deleted successfully")
