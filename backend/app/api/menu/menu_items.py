from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import MenuItemRepository, RestaurantRepository, MenuItemOptionsRepository, MenuItemAddonsRepository
from app.models.menu_items import MenuItem, validate_menu_item
from app.models.filters import GetMenuItemFilters, GetMenuItemOptionsFilters, GetMenuItemAddonsFilters
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.menu_items import MenuItemCreate, MenuItemUpdate, MenuItemListResponse, MenuItemSingleResponse

router = APIRouter(prefix="/menu_items", tags=["menu_items"])
menu_item_repo = MenuItemRepository()
restaurant_repo = RestaurantRepository()
menu_item_options_repo = MenuItemOptionsRepository()
menu_item_addons_repo = MenuItemAddonsRepository()

@router.get("/", response_model=MenuItemListResponse)
def get_menu_items(filters: GetMenuItemFilters = Depends(), db: Session = Depends(get_db)):
    menu_items = menu_item_repo.get(db, filters=filters)
    if not menu_items:
        raise NotFoundError("No menu items found")
    
    for menu_item in menu_items:
        options_filters = GetMenuItemOptionsFilters(menu_item_id=menu_item.id)
        menu_item.options = menu_item_options_repo.get(db, filters=options_filters)
        
        addons_filters = GetMenuItemAddonsFilters(menu_item_id=menu_item.id)
        menu_item.addons = menu_item_addons_repo.get(db, filters=addons_filters)
    
    return MenuItemListResponse(data=menu_items)

@router.post("/", response_model=MenuItemSingleResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    try:
        menu_item_obj = MenuItem(**menu_item.dict())
        validate_menu_item(menu_item_obj)

        restaurant = restaurant_repo.get(db, id=menu_item.restaurant_id)
        if not restaurant:
            raise NotFoundError(f"Restaurant {menu_item.restaurant_id} not found")

        created = menu_item_repo.create(db, obj_in=menu_item)
        return MenuItemSingleResponse(data=created, message="Menu item created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=MenuItemSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_menu_item(menu_item_data: MenuItemUpdate, menu_item_id: str = Query(...), db: Session = Depends(get_db)):
    menu_item = menu_item_repo.get(db, id=menu_item_id)
    if not menu_item:
        raise NotFoundError(f"Menu item {menu_item_id} not found")
    try:
        updated = menu_item_repo.update(db, db_obj=menu_item, obj_in=menu_item_data)
        return MenuItemSingleResponse(data=updated, message="Menu item updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{menu_item_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_menu_item(menu_item_id: str, db: Session = Depends(get_db)):
    menu_item = menu_item_repo.delete(db, id=menu_item_id)
    if not menu_item:
        raise NotFoundError(f"Menu item {menu_item_id} not found")
    return SuccessResponse(message="Menu item deleted successfully")