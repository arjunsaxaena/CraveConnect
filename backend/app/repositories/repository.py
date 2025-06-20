from app.repositories.base import BaseRepository
from app.models.user import User
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.reviews import Review
from app.models.payment import Payment
from app.models.favorites import Favorites
from app.models.menu_items import MenuItem
from app.models.menu_item_addons import MenuItemAddons
from app.models.menu_item_embedding import MenuItemEmbedding
from app.models.menu_item_options import MenuItemOptions
from app.models.notification import Notification
from app.models.order_assignments import OrderAssignments
from app.models.promotions import Promotion
from app.models.queries import Queries
from app.models.recommendation import Recommendation
from app.models.file import File
from app.models.addons import Addons
from app.models.delivery_person import DeliveryPerson
from app.models.user_preferences import UserPreferences



class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

class OrderRepository(BaseRepository):
    def __init__(self):
        super().__init__(Order)

class RestaurantRepository(BaseRepository):
    def __init__(self):
        super().__init__(Restaurant)

class ReviewRepository(BaseRepository):
    def __init__(self):
        super().__init__(Review)

class PaymentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Payment)

class FavoritesRepository(BaseRepository):
    def __init__(self):
        super().__init__(Favorites)

class MenuItemRepository(BaseRepository):
    def __init__(self):
        super().__init__(MenuItem)

class MenuItemAddonsRepository(BaseRepository):
    def __init__(self):
        super().__init__(MenuItemAddons)

class MenuItemEmbeddingRepository(BaseRepository):
    def __init__(self):
        super().__init__(MenuItemEmbedding)

class MenuItemOptionsRepository(BaseRepository):
    def __init__(self):
        super().__init__(MenuItemOptions)

class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)

class OrderAssignmentsRepository(BaseRepository):
    def __init__(self):
        super().__init__(OrderAssignments)

class PromotionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Promotion)

class QueriesRepository(BaseRepository):
    def __init__(self):
        super().__init__(Queries)

class RecommendationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Recommendation)

class FileRepository(BaseRepository):
    def __init__(self):
        super().__init__(File)

class AddonsRepository(BaseRepository):
    def __init__(self):
        super().__init__(Addons)

class DeliveryPersonRepository(BaseRepository):
    def __init__(self):
        super().__init__(DeliveryPerson)

class UserPreferencesRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserPreferences)
