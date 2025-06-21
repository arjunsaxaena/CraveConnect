from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.repositories.repository import OrderRepository, UserRepository, RestaurantRepository
from app.models.order import Order, validate_order
from app.models.filters import GetOrderFilters
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.schemas.orders import OrderCreate, OrderUpdate, OrderListResponse, OrderSingleResponse

router = APIRouter(prefix="/orders", tags=["orders"])
order_repo = OrderRepository()
user_repo = UserRepository()
restaurant_repo = RestaurantRepository()

@router.get("/", response_model=OrderListResponse, responses={404: {"model": ErrorResponse}})
def list_orders(filters: GetOrderFilters = Depends(), db: Session = Depends(get_db)):
    orders = order_repo.get(db, filters=filters)
    if not orders:
        raise NotFoundError("No orders found")
    return OrderListResponse(data=orders)

@router.post("/", response_model=OrderSingleResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": ErrorResponse}})
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    try:
        order_obj = Order(**order_in.dict())
        validate_order(order_obj)

        user = user_repo.get(db, id=order_in.user_id)
        if not user:
            raise NotFoundError(f"User {order_in.user_id} not found")

        restaurant = restaurant_repo.get(db, id=order_in.restaurant_id)
        if not restaurant:
            raise NotFoundError(f"Restaurant {order_in.restaurant_id} not found")

        created = order_repo.create(db, obj_in=order_in)
        return OrderSingleResponse(data=created, message="Order created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=OrderSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_order(order_id: str = Query(...), order_in: OrderUpdate = None, db: Session = Depends(get_db)):
    order = order_repo.get(db, id=order_id)
    if not order:
        raise NotFoundError(f"Order {order_id} not found")

    update_data = order_in.dict(exclude_unset=True)

    if "total_price" in update_data and update_data["total_price"] != order.total_price:
        raise BadRequestError("Total price cannot be updated")

    updated = order_repo.update(db, db_obj=order, obj_in=order_in)
    return OrderSingleResponse(data=updated, message="Order updated successfully")

@router.delete("/{order_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_order(order_id: str, db: Session = Depends(get_db)):
    order = order_repo.get(db, id=order_id)
    if not order:
        raise NotFoundError(f"Order {order_id} not found")
    order_repo.delete(db, id=order_id)
    return SuccessResponse(message="Order deleted successfully")