import json
import time
from typing import List, Dict
from app.config import logger, TEXT_MODEL, VISION_MODEL

def extract_json_from_response(text: str) -> str:
    if not text:
        logger.warning("Empty response from LLM")
        return "[]"
        
    json_str = text.strip()
    
    if "```json" in json_str:
        parts = json_str.split("```json")
        if len(parts) > 1:
            json_str = parts[1].split("```")[0].strip()
    elif "```" in json_str:
        parts = json_str.split("```")
        if len(parts) > 1:
            json_str = parts[1].strip()
    
    json_str = json_str.strip("[]")
    
    if not json_str.startswith("["):
        json_str = "[" + json_str
    if not json_str.endswith("]"):
        json_str = json_str + "]"
        
    if json_str.strip() == "[]":
        logger.warning("Extracted empty JSON array")

    return json_str

def parse_menu_text(menu_text: str) -> List[Dict]:
    if not menu_text.strip():
        logger.error("No text to parse")
        return []
        
    try:
        prompt = f"""
        You are a data extraction expert specializing in restaurant menus. You're working with a cafe/restaurant menu that has categories like COFFEES, COLD BREWS, HOT BEVERAGES, etc.

        Extract menu items from this text, paying special attention to:
        1. Item name
        2. Description in parentheses
        3. Price (usually appears at right side of each item, e.g. "90/-", "150/-")
        4. Category headers (like "COFFEES", "COLD BREWS", etc.)

        Here's the text from the menu:

        {menu_text}

        Format each item as a JSON object with:
        - name: Item name (string)
        - description: Description in parentheses if available, or null
        - price: Price as a number only (remove "/-" suffix)
        - category: Category name if available (COFFEES, COLD BREWS, etc.)

        For example:
        [
          {{"name": "Café Americano", "description": "Black Coffee", "price": 90, "category": "COFFEES"}},
          {{"name": "Happiness", "description": "Cappuccino Prepared By Freshly Grounded Coffee Beans Imported From Malta", "price": 130, "category": "COFFEES"}}
        ]

        Return a JSON array ONLY, with no other text or explanations.
        """
        
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        response = make_api_request_with_retry(
            TEXT_MODEL.generate_content,
            contents
        )
        
        json_str = extract_json_from_response(response.text)
        
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Invalid JSON: {json_str[:200]}")
            return []
            
    except Exception as e:
        logger.error(f"Error parsing menu with LLM: {e}")
        return []

def parse_menu_image(image_data: bytes) -> List[Dict]:
    try:
        prompt = """
        You're analyzing a restaurant/cafe menu image. Extract ALL menu items with their details.
        
        Pay close attention to:
        1. Item names (like "Café Americano", "Hazelnut Latte")
        2. Descriptions in parentheses (like "(Black Coffee)")
        3. Prices (usually shown on the right, like "90/-", "140/-")
        4. Category headers (like "COFFEES", "COLD BREWS", "HOT BEVERAGES")
        
        Format as a JSON array with each item having:
        - name: Item name
        - description: Description text (or null if none)
        - price: Price as a number only (remove "/-")
        - category: Category name the item belongs to
        
        Example expected format:
        [
          {"name": "Café Americano", "description": "Black Coffee", "price": 90, "category": "COFFEES"},
          {"name": "Happiness", "description": "Cappuccino Prepared By Freshly Grounded Coffee Beans Imported From Malta", "price": 130, "category": "COFFEES"}
        ]
        
        Return ONLY the JSON array, no other text.
        """
        
        contents = [
            {"role": "user", "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
            ]}
        ]
        
        response = make_api_request_with_retry(
            VISION_MODEL.generate_content,
            contents
        )
        
        json_str = extract_json_from_response(response.text)
        
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Vision API JSON: {e}")
            logger.error(f"Invalid JSON: {json_str[:200]}")
            return []
            
    except Exception as e:
        logger.error(f"Error with Vision API: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def make_api_request_with_retry(func, *args, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 3
                logger.warning(f"Rate limit hit, retrying in {wait_time}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                logger.error(f"API request failed: {error_str}")
                raise