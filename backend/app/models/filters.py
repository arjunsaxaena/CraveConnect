from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

# ** Order Filters **
class GetOrderFilters(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    restaurant_id: Optional[UUID] = None
    total_price: Optional[Decimal] = None

# ** User Filters **
class GetUserFilters(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    email: Optional[str] = None
    provider: Optional[str] = None

# ** Restaurant Filters **
class GetRestaurantFilters(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    owner_id: Optional[UUID] = None

# ** MenuItem Filters **
class GetMenuItemFilters(BaseModel):
    id: Optional[UUID] = None
    restaurant_id: Optional[UUID] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    allergens: Optional[List[str]] = None

# ** OrderAssignments Filters **
class GetOrderAssignmentsFilters(BaseModel):
    id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    delivery_person_id: Optional[UUID] = None

# ** DeliveryPerson Filters **
class GetDeliveryPersonFilters(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    vehicle_type: Optional[str] = None

# ** Notification Filters **
class GetNotificationFilters(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    title: Optional[str] = None
    seen: Optional[bool] = None

# ** Review Filters **
class GetReviewFilters(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    restaurant_id: Optional[UUID] = None
    rating: Optional[int] = None

# ** Promotion Filters **
class GetPromotionFilters(BaseModel):
    id: Optional[UUID] = None
    restaurant_id: Optional[UUID] = None
    title: Optional[str] = None
    discount_percent: Optional[Decimal] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None

# ** Payment Filters **
class GetPaymentFilters(BaseModel):
    id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    amount: Optional[Decimal] = None
    status: Optional[str] = None

# ** Favorites Filters **
class GetFavoritesFilters(BaseModel):
    user_id: Optional[UUID] = None
    menu_item_id: Optional[UUID] = None

# ** File Filters **
class GetFileFilters(BaseModel):
    id: Optional[UUID] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    uploaded_by: Optional[UUID] = None

# ** UserPreferences Filters **
class GetUserPreferencesFilters(BaseModel):
    user_id: Optional[UUID] = None
    preferred_cuisines: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    spice_tolerance: Optional[str] = None
    allergies: Optional[List[str]] = None

# ** Recommendation Filters **
class GetRecommendationFilters(BaseModel):
    id: Optional[UUID] = None
    query_id: Optional[UUID] = None
    menu_item_id: Optional[UUID] = None
    confidence_score: Optional[float] = None

# ** Queries Filters **
class GetQueriesFilters(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    query_text: Optional[str] = None
    feedback: Optional[str] = None

# ** MenuItemOptions Filters **
class GetMenuItemOptionsFilters(BaseModel):
    id: Optional[UUID] = None
    menu_item_id: Optional[UUID] = None
    name: Optional[str] = None
    price: Optional[Decimal] = None

# ** MenuItemAddons Filters **
class GetMenuItemAddonsFilters(BaseModel):
    menu_item_id: Optional[UUID] = None
    addon_id: Optional[UUID] = None

# ** Addons Filters **
class GetAddonsFilters(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    price: Optional[Decimal] = None

# ** MenuItemEmbedding Filters **
class GetMenuItemEmbeddingFilters(BaseModel):
    menu_item_id: Optional[UUID] = None

# ** MenuItemEmbedding Filters **
class GetMenuItemEmbeddingFilters(BaseModel):
    menu_item_id: Optional[UUID] = None