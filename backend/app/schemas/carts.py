from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from .cart_items import CartItemOut


class CartCreate(BaseModel):
    user_id: UUID
    restaurant_id: UUID
    meta: Optional[dict] = None


class CartUpdate(BaseModel):
    meta: Optional[dict] = None


class CartOut(BaseModel):
    id: UUID
    user_id: UUID
    restaurant_id: UUID
    meta: Optional[dict] = None
    items: List[CartItemOut] = []


class AddToCartRequest(BaseModel):
    menu_item_id: UUID
    quantity: int = 1
    base_price: Decimal
    special_instructions: Optional[str] = None
    addons: List[dict] = []


class CartSummary(BaseModel):
    cart: CartOut
    total_amount: Decimal
    item_count: int
    restaurant_name: Optional[str] = None
