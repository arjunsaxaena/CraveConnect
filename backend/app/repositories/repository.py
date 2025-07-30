from app.repositories.base import BaseRepository
from app.models.user import User
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.reviews import Review
from app.models.payment import PaymentHistory
from app.models.favorites import Favorites
from app.models.menu_items import MenuItem
from app.models.menu_item_addons import MenuItemAddons
from app.models.menu_item_embedding import MenuItemEmbedding
from app.models.notification import Notification
from app.models.order_assignments import OrderAssignments
from app.models.promotions import Promotion
from app.models.queries import Queries
from app.models.recommendation import Recommendation
from app.models.file import File
from app.models.addons import Addons
from app.models.delivery_persons import DeliveryPerson
from app.models.user_preferences import UserPreferences
from app.models.address import Address
from sqlalchemy import text
from sqlalchemy.orm import Session


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
        super().__init__(PaymentHistory)


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

    def get_top_k_similar(self, db: Session, query_embedding: list, k: int = 5):
        sql = text(
            "SELECT menu_item_id, (embedding <-> (:embedding)::vector) as distance FROM menu_item_embeddings "
            "ORDER BY distance ASC LIMIT :k"
        )
        result = db.execute(sql, {"embedding": query_embedding, "k": k})
        return [(row[0], 1.0 / (1.0 + row[1])) for row in result.fetchall()]


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


class AddressRepository(BaseRepository):
    def __init__(self):
        super().__init__(Address)
