import json
import time
from typing import List, Dict
from app.config import logger, TEXT_MODEL, VISION_MODEL

def extract_json_from_response(text: str) -> str:
    """Extract JSON from an LLM response that may contain markdown formatting."""
    json_str = text.strip()
    
    # Handle markdown code blocks
    if "```json" in json_str:
        # Extract between ```json and ```
        parts = json_str.split("```json")
        if len(parts) > 1:
            json_str = parts[1].split("```")[0].strip()
    elif "```" in json_str:
        # Extract between ``` and ```
        parts = json_str.split("```")
        if len(parts) > 1:
            json_str = parts[1].strip()
    
    # Remove any leading/trailing brackets if the response tried to format as a code block without markdown
    json_str = json_str.strip("[]")
    
    # Ensure it's a valid JSON array
    if not json_str.startswith("["):
        json_str = "[" + json_str
    if not json_str.endswith("]"):
        json_str = json_str + "]"
        
    logger.info(f"Extracted JSON: {json_str[:100]}...")
    return json_str

def parse_menu_text(menu_text: str) -> List[Dict]:
    """Parse menu text using Gemini LLM to extract structured menu items."""
    if not menu_text.strip():
        logger.error("No text to parse")
        return []
        
    try:
        prompt = f"""
        You are a data extraction expert specializing in restaurant menus. Extract menu items from this text:

        {menu_text}

        Format each item as a JSON object with:
        - name: Item name (string)
        - description: Item description if available, or null
        - price: Price as a number only (no currency symbols)
        - category: Category name if available, or null
        - size: Size name if multiple sizes exist, or null

        Return a JSON array ONLY, with no other text, explanation, or markdown:
        [
          {{"name": "Margherita", "description": "Classic cheese pizza", "price": 150, "category": "Hand Toasted Pizzas", "size": "8\""}},
          {{"name": "C4 Margherita", "description": "Extra Cheese on Cheese", "price": 200, "category": "Hand Toasted Pizzas", "size": "8\""}}
        ]
        """
        
        # Updated code with retry logic
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        response = make_api_request_with_retry(
            TEXT_MODEL.generate_content,
            contents
        )
        
        logger.info(f"LLM raw response preview: {str(response.text)[:100]}")
        
        # Extract JSON from the response
        json_str = extract_json_from_response(response.text)
        
        try:
            data = json.loads(json_str)
            logger.info(f"Successfully parsed JSON with {len(data)} items")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Invalid JSON: {json_str[:200]}")
            return []
            
    except Exception as e:
        logger.error(f"Error parsing menu with LLM: {e}")
        return []

def parse_menu_image(image_data: bytes) -> List[Dict]:
    """Direct extraction from image using Gemini Vision."""
    try:
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": image_data
            }
        ]
        
        prompt = """
        Extract all menu items from this restaurant menu image.
        
        Return ONLY a JSON array with each item having these fields:
        - name: Item name (string)
        - description: Item description if available, or null
        - price: Price as a number only (no currency symbols)
        - category: Category name if available, or null
        - size: Size name if multiple sizes exist, or null
        
        Example format:
        [
          {"name": "Margherita", "description": "Classic cheese pizza", "price": 150, "category": "Hand Toasted Pizzas", "size": "8\""},
          {"name": "C4 Margherita", "description": "Extra Cheese on Cheese", "price": 200, "category": "Hand Toasted Pizzas", "size": "8\""}
        ]
        """
        
        # Updated code with retry logic and proper parameter format for gemini-1.5-flash
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
        
        logger.info(f"Vision API raw response preview: {str(response.text)[:100]}")
        
        # Extract JSON from the response
        json_str = extract_json_from_response(response.text)
        
        try:
            data = json.loads(json_str)
            logger.info(f"Successfully parsed Vision API JSON with {len(data)} items")
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
    """Helper function to handle rate limits with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 3  # Exponential backoff
                logger.warning(f"Rate limit hit, retrying in {wait_time}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                logger.error(f"API request failed: {error_str}")
                raise