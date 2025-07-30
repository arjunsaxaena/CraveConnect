from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from .cart_item_addons import CartItemAddonOut


class CartItemCreate(BaseModel):
    cart_id: UUID
    menu_item_id: UUID
    quantity: int = 1
    base_price: Decimal
    special_instructions: Optional[str] = None
    meta: Optional[dict] = None


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    base_price: Optional[Decimal] = None
    special_instructions: Optional[str] = None
    meta: Optional[dict] = None


class CartItemOut(BaseModel):
    id: UUID
    cart_id: UUID
    menu_item_id: UUID
    quantity: int
    base_price: Decimal
    special_instructions: Optional[str] = None
    meta: Optional[dict] = None
    addons: List[CartItemAddonOut] = []


class CartItemListResponse(BaseModel):
    data: List[CartItemOut]
    message: str = "Cart items fetched successfully"


class CartItemSingleResponse(BaseModel):
    data: CartItemOut
    message: str = "Cart item fetched successfully"
