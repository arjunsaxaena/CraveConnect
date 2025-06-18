from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

# ** Order Filters **
class GetOrderFilters(BaseModel):
    id: Optional[UUID]
    user_id: Optional[UUID]
    restaurant_id: Optional[UUID]
    total_price: Optional[Decimal]

# ** User Filters **
class GetUserFilters(BaseModel):
    id: Optional[UUID]
    name: Optional[str]
    email: Optional[str]
    provider: Optional[str]

# ** Restaurant Filters **
class GetRestaurantFilters(BaseModel):
    id: Optional[UUID]
    name: Optional[str]
    owner_id: Optional[UUID]

# ** MenuItem Filters **
class GetMenuItemFilters(BaseModel):
    id: Optional[UUID]
    restaurant_id: Optional[UUID]
    name: Optional[str]
    tags: Optional[List[str]]
    allergens: Optional[List[str]]

# ** OrderAssignments Filters **
class GetOrderAssignmentsFilters(BaseModel):
    id: Optional[UUID]
    order_id: Optional[UUID]
    delivery_person_id: Optional[UUID]

# ** DeliveryPerson Filters **
class GetDeliveryPersonFilters(BaseModel):
    id: Optional[UUID]
    name: Optional[str]
    phone_number: Optional[str]
    vehicle_type: Optional[str]

# ** Notification Filters **
class GetNotificationFilters(BaseModel):
    id: Optional[UUID]
    user_id: Optional[UUID]
    title: Optional[str]
    seen: Optional[bool]

# ** Review Filters **
class GetReviewFilters(BaseModel):
    id: Optional[UUID]
    user_id: Optional[UUID]
    restaurant_id: Optional[UUID]
    rating: Optional[int]

# ** Promotion Filters **
class GetPromotionFilters(BaseModel):
    id: Optional[UUID]
    restaurant_id: Optional[UUID]
    title: Optional[str]
    discount_percent: Optional[Decimal]
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]

# ** Payment Filters **
class GetPaymentFilters(BaseModel):
    id: Optional[UUID]
    order_id: Optional[UUID]
    amount: Optional[Decimal]
    status: Optional[str]

# ** Favorites Filters **
class GetFavoritesFilters(BaseModel):
    user_id: Optional[UUID]
    menu_item_id: Optional[UUID]

# ** File Filters **
class GetFileFilters(BaseModel):
    id: Optional[UUID]
    file_url: Optional[str]
    file_type: Optional[str]
    uploaded_by: Optional[UUID]

# ** UserPreferences Filters **
class GetUserPreferencesFilters(BaseModel):
    user_id: Optional[UUID]
    preferred_cuisines: Optional[List[str]]
    dietary_restrictions: Optional[List[str]]
    spice_tolerance: Optional[str]
    allergies: Optional[List[str]]

# ** Recommendation Filters **
class GetRecommendationFilters(BaseModel):
    id: Optional[UUID]
    query_id: Optional[UUID]
    menu_item_id: Optional[UUID]
    confidence_score: Optional[float]

# ** Queries Filters **
class GetQueriesFilters(BaseModel):
    id: Optional[UUID]
    user_id: Optional[UUID]
    query_text: Optional[str]
    feedback: Optional[str]

# ** MenuItemOptions Filters **
class GetMenuItemOptionsFilters(BaseModel):
    id: Optional[UUID]
    menu_item_id: Optional[UUID]
    name: Optional[str]
    price: Optional[Decimal]

# ** MenuItemAddons Filters **
class GetMenuItemAddonsFilters(BaseModel):
    menu_item_id: Optional[UUID]
    addon_id: Optional[UUID]

# ** Addons Filters **
class GetAddonsFilters(BaseModel):
    id: Optional[UUID]
    name: Optional[str]
    price: Optional[Decimal]

# ** MenuItemEmbedding Filters **
class GetMenuItemEmbeddingFilters(BaseModel):
    menu_item_id: Optional[UUID]

# ** MenuItemEmbedding Filters **
class GetMenuItemEmbeddingFilters(BaseModel):
    menu_item_id: Optional[UUID] 