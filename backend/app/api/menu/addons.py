from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.repository import AddonsRepository
from app.models.addons import Addons, validate_addons
from app.models.filters import GetAddonsFilters
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.addons import AddonsCreate, AddonsUpdate, AddonsListResponse, AddonsSingleResponse

router = APIRouter(prefix="/addons", tags=["addons"])
addon_repo = AddonsRepository()

@router.get("/", response_model=AddonsListResponse)
def get_addons(filters: GetAddonsFilters = Depends(), db: Session = Depends(get_db)):
    addons = addon_repo.get(db, filters=filters)
    if not addons:
        raise NotFoundError("No addons found")
    return AddonsListResponse(data=addons)

@router.post("/", response_model=AddonsSingleResponse, status_code=status.HTTP_201_CREATED)
def create_addon(addon: AddonsCreate, db: Session = Depends(get_db)):
    try:
        addon_obj = Addons(**addon.dict())
        validate_addons(addon_obj)

        created = addon_repo.create(db, obj_in=addon)
        return AddonsSingleResponse(data=created, message="Addon created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=AddonsSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_addon(addon_data: AddonsUpdate, addon_id: str, db: Session = Depends(get_db)):
    addon = addon_repo.get(db, id=addon_id)
    if not addon:
        raise NotFoundError(f"Addon {addon_id} not found")
    try:
        updated = addon_repo.update(db, db_obj=addon, obj_in=addon_data)
        return AddonsSingleResponse(data=updated, message="Addon updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{addon_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_addon(addon_id: str, db: Session = Depends(get_db)):
    addon = addon_repo.delete(db, id=addon_id)
    if not addon:
        raise NotFoundError(f"Addon {addon_id} not found")
    return SuccessResponse(message="Addon deleted successfully")