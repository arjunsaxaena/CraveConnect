from sqlalchemy.orm import Session
from uuid import UUID
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import cohere
import requests
import backoff

from app.repositories.repository import (
    MenuItemRepository, 
    MenuItemEmbeddingRepository,
    RestaurantRepository
)
from app.schemas.menu_item_embedding import MenuItemEmbeddingCreate, MenuItemEmbeddingUpdate
from app.models.filters import GetMenuItemFilters
from app.core.errors import NotFoundError, BadRequestError
from app.core.config import settings
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    co = cohere.Client(settings.COHERE_API_KEY)
    logger.info("Cohere API client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Cohere API client: {e}")
    co = None


def create_text_for_embedding(menu_item) -> str:
    """
    Creates a rich text representation of menu item by combining various attributes
    for better embedding quality.
    """
    text_parts = [menu_item.name]
    
    if menu_item.description:
        text_parts.append(menu_item.description)
    
    if menu_item.tags and len(menu_item.tags) > 0:
        text_parts.append(" ".join(menu_item.tags))
    
    if menu_item.allergens and len(menu_item.allergens) > 0:
        text_parts.append("Allergens: " + ", ".join(menu_item.allergens))
    
    return " ".join(text_parts)


@backoff.on_exception(backoff.expo, 
                     (requests.exceptions.RequestException, Exception),
                     max_tries=3)
def generate_embedding(text: str) -> List[float]:
    """
    Generates a vector embedding using Cohere API with retry capability.
    """
    if not co:
        raise BadRequestError("Cohere API client is not available")
    
    try:
        response = co.embed(
            texts=[text],
            model='embed-english-light-v3.0',
            input_type='search_query'
        )
        embedding = response.embeddings[0]
        
        embedding_array = np.array(embedding)
        normalized_embedding = embedding_array / np.linalg.norm(embedding_array)
        
        return normalized_embedding.tolist()
    except Exception as e:
        logger.error(f"Error generating embedding with Cohere: {e}")
        raise BadRequestError(f"Failed to generate embedding: {str(e)}")


def create_menu_item_embedding(db: Session, menu_item_id: UUID) -> Dict[str, Any]:
    """
    Creates or updates embedding for a specific menu item
    """
    menu_item_repo = MenuItemRepository()
    embedding_repo = MenuItemEmbeddingRepository()

    menu_item = menu_item_repo.get(db, id=menu_item_id)
    if not menu_item:
        raise NotFoundError(f"Menu item with id {menu_item_id} not found")

    text_for_embedding = create_text_for_embedding(menu_item)
    embedding_vector = generate_embedding(text_for_embedding)
    
    existing_embeddings = embedding_repo.get(db, filters={"menu_item_id": menu_item_id})
    existing_embedding = existing_embeddings[0] if existing_embeddings else None
    
    if existing_embedding:
        embedding_update = MenuItemEmbeddingUpdate(embedding=embedding_vector)
        updated = embedding_repo.update(db, db_obj=existing_embedding, obj_in=embedding_update)
        return {"message": "Embedding updated successfully", "menu_item_id": str(menu_item_id)}
    else:
        embedding_create = MenuItemEmbeddingCreate(
            menu_item_id=menu_item_id,
            embedding=embedding_vector
        )
        created = embedding_repo.create(db, obj_in=embedding_create)
        return {"message": "Embedding created successfully", "menu_item_id": str(menu_item_id)}


def process_embedding_async(menu_item_id: UUID):
    """
    Standalone function that can be called by background workers or tasks.
    Opens its own database session.
    """
    db = None
    try:
        db = SessionLocal()
        result = create_menu_item_embedding(db, menu_item_id)
        logger.info(f"Async embedding processing completed for menu item {menu_item_id}: {result['message']}")
        return result
    except Exception as e:
        logger.error(f"Async embedding processing failed for menu item {menu_item_id}: {str(e)}")
        raise e
    finally:
        if db:
            db.close()


def create_embeddings_for_restaurant(db: Session, restaurant_id: UUID) -> Dict[str, Any]:
    """
    Creates or updates embeddings for all menu items of a restaurant
    """
    restaurant_repo = RestaurantRepository()
    menu_item_repo = MenuItemRepository()

    restaurant = restaurant_repo.get(db, id=restaurant_id)
    if not restaurant:
        raise NotFoundError(f"Restaurant with id {restaurant_id} not found")

    filters = GetMenuItemFilters(restaurant_id=restaurant_id)
    menu_items = menu_item_repo.get(db, filters=filters)
    
    if not menu_items:
        raise NotFoundError(f"No menu items found for restaurant with id {restaurant_id}")
    
    results = {
        "created": 0,
        "updated": 0,
        "failed": 0,
        "total": len(menu_items),
        "menu_items": []
    }
    
    for menu_item in menu_items:
        try:
            result = create_menu_item_embedding(db, menu_item.id)
            if "created" in result["message"].lower():
                results["created"] += 1
            else:
                results["updated"] += 1
            results["menu_items"].append({
                "id": str(menu_item.id),
                "name": menu_item.name,
                "status": "success"
            })
        except Exception as e:
            results["failed"] += 1
            results["menu_items"].append({
                "id": str(menu_item.id),
                "name": menu_item.name,
                "status": "failed",
                "error": str(e)
            })
    
    logger.info(f"Processed embeddings for restaurant {restaurant_id}: " 
                f"{results['created']} created, {results['updated']} updated, {results['failed']} failed")
    
    return results


def batch_create_embeddings(db: Session, menu_item_ids: Optional[List[UUID]] = None) -> Dict[str, Any]:
    """
    Creates or updates embeddings for a batch of menu items,
    or all menu items if no specific IDs are provided
    """
    menu_item_repo = MenuItemRepository()

    if menu_item_ids:
        menu_items = []
        for item_id in menu_item_ids:
            item = menu_item_repo.get(db, id=item_id)
            if item:
                menu_items.append(item)
    else:
        menu_items = menu_item_repo.get(db)
    
    if not menu_items:
        raise NotFoundError("No menu items found to process")
    
    results = {
        "created": 0,
        "updated": 0,
        "failed": 0,
        "total": len(menu_items),
        "menu_items": []
    }
    
    for menu_item in menu_items:
        try:
            result = create_menu_item_embedding(db, menu_item.id)
            if "created" in result["message"].lower():
                results["created"] += 1
            else:
                results["updated"] += 1
            results["menu_items"].append({
                "id": str(menu_item.id),
                "name": menu_item.name,
                "status": "success"
            })
        except Exception as e:
            results["failed"] += 1
            results["menu_items"].append({
                "id": str(menu_item.id),
                "name": menu_item.name,
                "status": "failed",
                "error": str(e)
            })
    
    logger.info(f"Batch processed {results['total']} menu items: "
               f"{results['created']} created, {results['updated']} updated, {results['failed']} failed")
    
    return results


def find_similar_menu_items(db: Session, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
    if not co:
        raise BadRequestError("Cohere API client is not available")
    try:
        query_embedding = generate_embedding(query_text)
        menu_item_repo = MenuItemRepository()
        
        from sqlalchemy import text
        from app.models.menu_item_embedding import MenuItemEmbedding
        from app.models.menu_items import MenuItem
    
        vector_str = f"'[{','.join(map(str, query_embedding))}]'"

        query = text(f"""
            SELECT 
                mi.id, 
                mi.name, 
                mi.description,
                mi.price,
                mi.tags,
                mi.allergens,
                mi.image_url,
                mi.restaurant_id,
                1 - (embedding <-> {vector_str}::vector) as similarity
            FROM 
                menu_item_embeddings mie
            JOIN 
                menu_items mi ON mie.menu_item_id = mi.id
            ORDER BY 
                embedding <-> {vector_str}::vector
            LIMIT {limit}
        """)
        
        result = db.execute(query)
        
        similar_items = []
        for row in result:
            menu_item_dict = {
                "menu_item_id": str(row.id),
                "name": row.name,
                "similarity": float(row.similarity),
                "menu_item": {
                    "id": str(row.id),
                    "name": row.name,
                    "description": row.description,
                    "price": row.price,
                    "tags": row.tags,
                    "allergens": row.allergens,
                    "image_url": row.image_url,
                    "restaurant_id": str(row.restaurant_id)
                }
            }
            similar_items.append(menu_item_dict)
        
        return similar_items
        
    except Exception as e:
        logger.error(f"Error finding similar menu items: {e}")
        raise BadRequestError(f"Failed to find similar menu items: {str(e)}")