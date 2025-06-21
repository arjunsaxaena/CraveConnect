from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import DeliveryPersonRepository, UserRepository
from app.models.delivery_persons import DeliveryPerson, validate_delivery_person
from app.models.filters import GetDeliveryPersonFilters
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.delivery_persons import DeliveryPersonCreate, DeliveryPersonUpdate, DeliveryPersonListResponse, DeliveryPersonSingleResponse

router = APIRouter(prefix="/delivery_persons", tags=["delivery_persons"])
delivery_person_repo = DeliveryPersonRepository()
user_repo = UserRepository()

@router.get("/", response_model=DeliveryPersonListResponse, responses={404: {"model": ErrorResponse}})
def list_delivery_persons(filters: GetDeliveryPersonFilters = Depends(), db: Session = Depends(get_db)):
    delivery_persons = delivery_person_repo.get(db, filters=filters)
    if not delivery_persons:
        raise NotFoundError("No delivery persons found")
    return DeliveryPersonListResponse(data=delivery_persons)

@router.post("/", response_model=DeliveryPersonSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_delivery_person(delivery_person_in: DeliveryPersonCreate, db: Session = Depends(get_db)):
    try:
        delivery_person_obj = DeliveryPerson(**delivery_person_in.dict())
        validate_delivery_person(delivery_person_obj)

        user = user_repo.get(db, id=delivery_person_in.user_id)
        if not user:
            raise NotFoundError(f"User {delivery_person_in.user_id} not found")

        created = delivery_person_repo.create(db, obj_in=delivery_person_in)
        return DeliveryPersonSingleResponse(data=created, message="Delivery person created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=DeliveryPersonSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_delivery_person(delivery_person_id: str = Query(...), delivery_person_in: DeliveryPersonUpdate = None, db: Session = Depends(get_db)):
    delivery_person = delivery_person_repo.get(db, id=delivery_person_id)
    if not delivery_person:
        raise NotFoundError(f"Delivery person {delivery_person_id} not found")
    
    update_data = delivery_person_in.dict(exclude_unset=True)

    if "name" in update_data and update_data["name"] != delivery_person.name:
        raise BadRequestError("Name cannot be updated")

    updated = delivery_person_repo.update(db, db_obj=delivery_person, obj_in=delivery_person_in)
    return DeliveryPersonSingleResponse(data=updated, message="Delivery person updated successfully")

@router.delete("/{delivery_person_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_delivery_person(delivery_person_id: str, db: Session = Depends(get_db)):
    delivery_person = delivery_person_repo.get(db, id=delivery_person_id)
    if not delivery_person:
        raise NotFoundError(f"Delivery person {delivery_person_id} not found")
    delivery_person_repo.delete(db, id=delivery_person_id)
    return SuccessResponse(message="Delivery person deleted successfully")
