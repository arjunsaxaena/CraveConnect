import os
import json
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Any, Optional
from PIL import Image
import pytesseract
import google.generativeai as genai
import numpy as np
import dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv("../../.env")

# Database connection parameters
DB_URL = os.getenv("DB_URL")

def connect_to_db():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def ocr_image(image_path: str) -> str:
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        logger.info(f"OCR extracted {len(text)} characters from image")
        return text
    except Exception as e:
        logger.error(f"OCR extraction error: {e}")
        raise

def gemini_parse_menu(raw_text: str, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)
        prompt = f"""
        You are a data extraction expert. Your task is to convert unstructured restaurant menu text (from OCR or scanned images) into structured data for a PostgreSQL database table called `MenuItems`. The table’s schema is:

        - id: UUID (unique identifier for each menu item, you can ignore this for now)
        - restaurant_id: UUID (not relevant in extraction, ignore)
        - name: VARCHAR(100) (dish name)
        - description: TEXT (dish description, may be missing)
        - price: DECIMAL(8,2) (price, always as a number, e.g., 199.00)
        - image_url: VARCHAR(255) (ignore for extraction, leave blank)
        - embedding_ref: VARCHAR(255) (ignore for extraction, leave blank)
        - created_at: TIMESTAMP (ignore for extraction)
        - updated_at: TIMESTAMP (ignore for extraction)

        **Menu items can have multiple sizes (like Regular, Medium, Large, S, M, L, 8", 11", 16", etc.), and each size has a different price. Some items have no sizes. Some items have categories (like "Veg Pizzas" or "Non-Veg Pizzas"). Some have descriptions, some do not. Sometimes sizes and prices are in columns, sometimes in a list, sometimes in parentheses. Layouts vary.**

        **Your job is:**
        1. Extract each menu item, its name, description (if present), and for each available size, a separate object with the size and price.
        2. If there are categories or sections, include them as a `"category"` field.
        3. Output a flat JSON array, where each object represents a single menu item for a single size. For items with multiple sizes, output one object per size.
        4. For items with only one price (no size), output a single object with `"size"` set to `null`.
        5. For all prices, output as a number (not as a string, no currency symbols or slashes).
        6. Ignore non-menu content, footers, disclaimers, "Add Ons", and upgrades unless they are formatted as main menu items.

        **Each JSON object should have these fields:**
        - name: string (e.g. "Margherita")
        - description: string or null (e.g. "Cheesy Classic" or null)
        - category: string or null (e.g. "Veg Pizzas" or null)
        - size: string or null (e.g. "Regular", "Medium", "Large", "S 8\"", "L 16\"", or null)
        - price: number (e.g. 199.00)

        **Output only the JSON array. Do not include explanations, markdown, or any other text.**

        **Menu text to extract:**
        {raw_text}
        """
        
        model = genai.GenerativeModel('gemini-2.0-pro')
        response = model.generate_content([prompt])
        
        # Extract JSON from response
        result = response.text
        # Find JSON content 
        if "```json" in result:
            json_content = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            json_content = result.split("```")[1].strip()
        else:
            json_content = result.strip()
            
        # Validate JSON
        json.loads(json_content)  # This will raise an error if invalid JSON
        logger.info(f"Successfully parsed menu with Gemini, found structured items")
        return json_content
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise

def map_to_menuitems(json_str: str, restaurant_id: str, image_path: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        items = json.loads(json_str)
        rows = []
        now = datetime.now()
        
        for item in items:
            # Combine size with name if size exists
            name = item['name']
            if 'size' in item and item['size']:
                name = f"{name} ({item['size']})"
            
            # Convert price to float, removing any currency symbol if present
            price_str = str(item["price"]).replace("$", "").replace("₹", "")
            
            row = {
                "id": str(uuid.uuid4()),
                "restaurant_id": restaurant_id,
                "name": name,
                "description": item.get("description", ""),
                "price": float(price_str),
                "image_path": image_path,
                "is_active": True,
                "created_at": now,
                "updated_at": now
            }
            rows.append(row)
            
        logger.info(f"Mapped {len(rows)} menu items to database schema")
        return rows
        
    except Exception as e:
        logger.error(f"Error mapping menu items: {e}")
        raise

def insert_menuitems(conn, menu_items: List[Dict[str, Any]]) -> List[str]:
    inserted_ids = []
    cursor = conn.cursor()
    
    try:
        for item in menu_items:
            cursor.execute("""
                INSERT INTO menu_items (
                    id, restaurant_id, name, description, price, 
                    image_path, is_active, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                item["id"], item["restaurant_id"], item["name"], 
                item["description"], item["price"], item["image_path"], 
                item["is_active"], item["created_at"], item["updated_at"]
            ))
            inserted_id = cursor.fetchone()[0]
            inserted_ids.append(inserted_id)
            
        conn.commit()
        logger.info(f"Successfully inserted {len(inserted_ids)} menu items into database")
        return inserted_ids
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Database insertion error: {e}")
        raise
    finally:
        cursor.close()

# def generate_embeddings(conn, menu_item_ids: List[str]):
#     """Generate embeddings for menu items and update database.
    
#     This is a placeholder. In a real implementation, you would:
#     1. Fetch menu items from database
#     2. Generate embeddings using an embedding model
#     3. Store embeddings in your vector database
#     4. Update the menu_items table with references to the embeddings
    
#     Args:
#         conn: Database connection
#         menu_item_ids: List of menu item IDs to generate embeddings for
#     """
#     cursor = conn.cursor(cursor_factory=RealDictCursor)
    
#     try:
#         # Fetch menu items
#         placeholders = ','.join(['%s'] * len(menu_item_ids))
#         cursor.execute(
#             f"SELECT id, name, description FROM menu_items WHERE id IN ({placeholders})",
#             menu_item_ids
#         )
#         items = cursor.fetchall()
        
#         # In a real implementation:
#         # 1. Generate embeddings
#         # 2. Store in vector database
#         # 3. Update menu_items with embedding references
        
#         logger.info(f"Embeddings would be generated for {len(items)} menu items")
        
#     except Exception as e:
#         logger.error(f"Error generating embeddings: {e}")
#         raise
#     finally:
#         cursor.close()

def process_menu_image(image_path: str, restaurant_id: str, gemini_api_key: str, 
                      menu_item_image_path: Optional[str] = None, 
                      generate_embeddings_flag: bool = False) -> List[Dict[str, Any]]:
    """Process a menu image and insert extracted items into the database."""
    # Step 1: OCR extraction
    raw_text = ocr_image(image_path)
    
    # Step 2: LLM structuring with Gemini
    menu_json = gemini_parse_menu(raw_text, gemini_api_key)
    
    # Step 3: Map to database schema
    menu_items = map_to_menuitems(menu_json, restaurant_id, menu_item_image_path)
    
    # Step 4: Insert into database
    conn = connect_to_db()
    try:
        inserted_ids = insert_menuitems(conn, menu_items)
        
        # Step 5: Generate embeddings if requested
        # if generate_embeddings_flag:
        #     generate_embeddings(conn, inserted_ids)
            
        return menu_items
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    # These would be provided by your application
    SAMPLE_IMAGE_PATH = "../uploads/menu_images/sample_menu.jpg"
    RESTAURANT_ID = "your-restaurant-uuid"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not os.path.exists(SAMPLE_IMAGE_PATH):
        logger.error(f"Image file not found: {SAMPLE_IMAGE_PATH}")
    elif not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment variables")
    else:
        try:
            menu_items = process_menu_image(
                SAMPLE_IMAGE_PATH, 
                RESTAURANT_ID,
                GEMINI_API_KEY
            )
            print(f"Processed {len(menu_items)} menu items")
            for item in menu_items:
                print(f"- {item['name']}: ${item['price']}")
        except Exception as e:
            logger.error(f"Error processing menu: {e}")
