from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import MenuItemOptionsRepository, MenuItemRepository
from app.models.menu_item_options import MenuItemOptions, validate_menu_item_options
from app.models.filters import GetMenuItemOptionsFilters
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.core.errors import NotFoundError, BadRequestError
from app.schemas.menu_item_options import MenuItemOptionCreate, MenuItemOptionUpdate, MenuItemOptionListResponse, MenuItemOptionSingleResponse

router = APIRouter(prefix="/menu_item_options", tags=["menu_item_options"])
menu_item_option_repo = MenuItemOptionsRepository()
menu_item_repo = MenuItemRepository()

@router.get("/", response_model=MenuItemOptionListResponse)
def get_menu_item_options(filters: GetMenuItemOptionsFilters = Depends(), db: Session = Depends(get_db)):
    menu_item_options = menu_item_option_repo.get(db, filters=filters)
    if not menu_item_options:
        raise NotFoundError("No menu item options found")
    return MenuItemOptionListResponse(data=menu_item_options)

@router.post("/", response_model=MenuItemOptionSingleResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item_option(menu_item_option: MenuItemOptionCreate, db: Session = Depends(get_db)):
    try:
        menu_item_option_obj = MenuItemOptions(**menu_item_option.dict())
        validate_menu_item_options(menu_item_option_obj)

        menu_item = menu_item_repo.get(db, id=menu_item_option.menu_item_id)
        if not menu_item:
            raise NotFoundError(f"Menu item {menu_item_option.menu_item_id} not found")

        created = menu_item_option_repo.create(db, obj_in=menu_item_option)
        return MenuItemOptionSingleResponse(data=created, message="Menu item option created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))


@router.patch("/", response_model=MenuItemOptionSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_menu_item_option(menu_item_option_data: MenuItemOptionUpdate, menu_item_option_id: str = Query(...), db: Session = Depends(get_db)):
    menu_item_option = menu_item_option_repo.get(db, id=menu_item_option_id)
    if not menu_item_option:
        raise NotFoundError(f"Menu item option {menu_item_option_id} not found")

    try:
        updated = menu_item_option_repo.update(db, db_obj=menu_item_option, obj_in=menu_item_option_data)
        return MenuItemOptionSingleResponse(data=updated, message="Menu item option updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{menu_item_option_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_menu_item_option(menu_item_option_id: str, db: Session = Depends(get_db)):
    menu_item_option = menu_item_option_repo.get(db, id=menu_item_option_id)
    if not menu_item_option:
        raise NotFoundError(f"Menu item option {menu_item_option_id} not found")
    menu_item_option_repo.delete(db, db_obj=menu_item_option)
    return SuccessResponse(message="Menu item option deleted successfully")