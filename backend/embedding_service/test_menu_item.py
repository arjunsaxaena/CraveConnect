import os
import sys
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_menu_item")

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.data_pipeline_service.app.embedding import generate_menu_item_embedding
from backend.data_pipeline_service.app.schemas import map_to_menu_items, validate_menu_items
from backend.data_pipeline_service.app.api import send_menu_items_with_embeddings

def test_menu_item_processing():
    """Test the menu item processing with size field and embeddings"""
    logger.info("Testing menu item processing with size field")
    
    # Create a sample restaurant ID
    restaurant_id = "test-restaurant-123"
    
    # Create sample extracted menu items with different sizes
    extracted_items = [
        {
            "name": "Cappuccino",
            "price": 3.99,
            "description": "Rich espresso with steamed milk and foam",
            "category": "Coffee",
            "size": "Small"
        },
        {
            "name": "Cappuccino",
            "price": 4.99,
            "description": "Rich espresso with steamed milk and foam",
            "category": "Coffee",
            "size": "Medium"
        },
        {
            "name": "Cappuccino",
            "price": 5.99,
            "description": "Rich espresso with steamed milk and foam",
            "category": "Coffee", 
            "size": "Large"
        },
        {
            "name": "Espresso",
            "price": 2.99,
            "description": "Single shot of espresso",
            "category": "Coffee"
        }
    ]
    
    logger.info(f"Sample extracted items: {json.dumps(extracted_items, indent=2)}")
    
    # Map to menu items
    menu_items = map_to_menu_items(restaurant_id, extracted_items)
    logger.info(f"Mapped {len(menu_items)} menu items")
    
    # Validate menu items
    valid, error_msg = validate_menu_items(menu_items)
    if not valid:
        logger.error(f"Validation failed: {error_msg}")
        return
    else:
        logger.info("Validation passed")
    
    # Generate embeddings
    embedding_success_count = 0
    for item in menu_items:
        # Print item for debugging
        logger.info(f"Processing item for embedding: {item}")
        
        embedding = generate_menu_item_embedding(item)
        if embedding:
            item["embedding"] = embedding
            embedding_success_count += 1
            logger.info(f"Generated embedding for: {item['name']}, Size: {item['size']}")
    
    if embedding_success_count == 0:
        logger.error("Failed to generate any embeddings")
        return
    else:
        logger.info(f"Generated {embedding_success_count} embeddings out of {len(menu_items)} menu items")
    
    # Print sample of menu items with embeddings
    for i, item in enumerate(menu_items):
        item_copy = item.copy()
        if "embedding" in item_copy:
            item_copy["embedding"] = f"[{len(item_copy['embedding'])} dimensions]" if item_copy["embedding"] else None
        logger.info(f"Menu item {i+1}: {json.dumps(item_copy, indent=2)}")
    
    # Test API sending if needed (commented out to avoid actual API calls)
    # success = send_menu_items_with_embeddings(menu_items)
    # logger.info(f"API send result: {success}")

if __name__ == "__main__":
    test_menu_item_processing() 