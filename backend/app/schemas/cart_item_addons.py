from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal


class CartItemAddonCreate(BaseModel):
    cart_item_id: UUID
    addon_id: UUID
    quantity: int = 1
    addon_price: Decimal
    meta: Optional[dict] = None


class CartItemAddonUpdate(BaseModel):
    quantity: Optional[int] = None
    addon_price: Optional[Decimal] = None
    meta: Optional[dict] = None


class CartItemAddonOut(BaseModel):
    id: UUID
    cart_item_id: UUID
    addon_id: UUID
    quantity: int
    addon_price: Decimal
    meta: Optional[dict] = None


class CartItemAddonListResponse(BaseModel):
    data: List[CartItemAddonOut]
    message: str = "Cart item addons fetched successfully"


class CartItemAddonSingleResponse(BaseModel):
    data: CartItemAddonOut
    message: str = "Cart item addon fetched successfully"
