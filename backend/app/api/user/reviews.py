from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import ReviewRepository, UserRepository, RestaurantRepository
from app.models.reviews import Review, validate_review
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.reviews import ReviewCreate, ReviewUpdate, ReviewListResponse, ReviewSingleResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])
review_repo = ReviewRepository()
user_repo = UserRepository()
restaurant_repo = RestaurantRepository()

@router.get("/", response_model=ReviewListResponse, responses={404: {"model": ErrorResponse}})
def list_reviews(db: Session = Depends(get_db)):
    reviews = review_repo.get(db)
    if not reviews:
        raise NotFoundError("No reviews found")
    return ReviewListResponse(data=reviews)

@router.post("/", response_model=ReviewSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_review(review_in: ReviewCreate, db: Session = Depends(get_db)):
    try:
        review_obj = Review(**review_in.dict())
        validate_review(review_obj)

        user = user_repo.get(db, id=review_in.user_id)
        if not user:
            raise NotFoundError(f"User {review_in.user_id} not found")

        restaurant = restaurant_repo.get(db, id=review_in.restaurant_id)
        if not restaurant:
            raise NotFoundError(f"Restaurant {review_in.restaurant_id} not found")

        created = review_repo.create(db, obj_in=review_in)
        return ReviewSingleResponse(data=created, message="Review created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=ReviewSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_review(review_id: str = Query(...), review_in: ReviewUpdate = None, db: Session = Depends(get_db)):
    review = review_repo.get(db, id=review_id)
    if not review:
        raise NotFoundError(f"Review {review_id} not found")
    try:
        updated = review_repo.update(db, db_obj=review, obj_in=review_in)
        return ReviewSingleResponse(data=updated, message="Review updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{review_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_review(review_id: str, db: Session = Depends(get_db)):
    review = review_repo.get(db, id=review_id)
    if not review:
        raise NotFoundError(f"Review {review_id} not found")
    review_repo.delete(db, id=review_id)
    return SuccessResponse(message=f"Review {review_id} deleted successfully")
