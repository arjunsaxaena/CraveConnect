from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from app.repositories.repository import AddressRepository
from app.models.address import Address
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.address import AddressCreate, AddressUpdate, AddressListResponse, AddressSingleResponse
from uuid import UUID

router = APIRouter(prefix="/addresses", tags=["addresses"])
address_repo = AddressRepository()

@router.get("/", response_model=AddressListResponse, responses={404: {"model": ErrorResponse}})
def get_addresses(
    user_id: UUID = Query(None),
    restaurant_id: UUID = Query(None),
    db: Session = Depends(get_db)
):
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if restaurant_id:
        filters["restaurant_id"] = restaurant_id
    addresses = address_repo.get(db, filters=filters)
    if not addresses:
        raise NotFoundError("No addresses found")
    return AddressListResponse(data=addresses)

@router.post("/", response_model=AddressSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_address(
    address_in: AddressCreate,
    user_id: UUID = Query(None),
    restaurant_id: UUID = Query(None),
    db: Session = Depends(get_db)
):
    try:
        address_data = address_in.model_dump() if hasattr(address_in, 'model_dump') else address_in.dict()
        if user_id:
            address_data["user_id"] = user_id
        if restaurant_id:
            address_data["restaurant_id"] = restaurant_id
        created = address_repo.create(db, obj_in=AddressCreate(**address_data))
        return AddressSingleResponse(data=created, message="Address created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=AddressSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_address(
    address_id: UUID = Query(...),
    address_in: AddressUpdate = None,
    user_id: UUID = Query(None),
    restaurant_id: UUID = Query(None),
    db: Session = Depends(get_db)
):
    address = address_repo.get(db, id=address_id)
    if not address:
        raise NotFoundError(f"Address {address_id} not found")
    if user_id and address.user_id != user_id:
        raise NotFoundError(f"Address {address_id} not found for this user")
    if restaurant_id and address.restaurant_id != restaurant_id:
        raise NotFoundError(f"Address {address_id} not found for this restaurant")
    try:
        updated = address_repo.update(db, db_obj=address, obj_in=address_in)
        return AddressSingleResponse(data=updated, message="Address updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{address_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_address(
    address_id: UUID = Path(...),
    user_id: UUID = Query(None),
    restaurant_id: UUID = Query(None),
    db: Session = Depends(get_db)
):
    address = address_repo.get(db, id=address_id)
    if not address:
        raise NotFoundError(f"Address {address_id} not found")
    if user_id and address.user_id != user_id:
        raise NotFoundError(f"Address {address_id} not found for this user")
    if restaurant_id and address.restaurant_id != restaurant_id:
        raise NotFoundError(f"Address {address_id} not found for this restaurant")
    address_repo.delete(db, id=address_id)
    return SuccessResponse(message=f"Address {address_id} deleted successfully") 