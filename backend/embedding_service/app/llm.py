import json
import base64
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import logger, GEMINI_API_KEY, LLM_MODEL, GENERATION_CONFIG

# Configure Google API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize models
vision_model = None
text_model = None

if GEMINI_API_KEY:
    try:
        common_config = {
            "google_api_key": GEMINI_API_KEY,
            "convert_system_message_to_human": True,
            "credentials": None,
            "generation_config": GENERATION_CONFIG
        }
        
        vision_model = ChatGoogleGenerativeAI(model=LLM_MODEL, **common_config)
        text_model = ChatGoogleGenerativeAI(model=LLM_MODEL, **common_config)
        
        logger.info(f"LLM models initialized: {LLM_MODEL}")
    except Exception as e:
        logger.error(f"Error initializing LLM models: {str(e)}")
else:
    logger.warning("No Gemini API key provided. LLM functionality disabled.")

def encode_image(image_data: bytes) -> str:
    """Encode image data as base64 string."""
    return base64.b64encode(image_data).decode('utf-8')

def parse_menu_text(menu_text: str) -> List[Dict[str, Any]]:
    """Parse menu text and extract menu items for any type of menu."""
    if not text_model or not menu_text.strip():
        return []
        
    prompt = """
    Extract all menu items from the following text. This could be any type of menu (food, beverages, etc.).
    
    Return a JSON array of objects with these fields:
    - name (required): item name
    - price (required): numeric price (just the number, no currency symbols)
    - description (optional): item description
    - category (optional): menu category (e.g., "COFFEES", "HOT BEVERAGES", etc.)
    - size (optional): portion size if applicable
    
    Example output format:
    [
      {
        "name": "Café Americano",
        "description": "Black Coffee",
        "price": 90,
        "category": "COFFEES"
      },
      {
        "name": "Hot Chocolate",
        "description": "Hershey's Cocoa Syrup Mixed With Warm Steamed Milk, Sprinkled With Chocolate Powder",
        "price": 130,
        "category": "HOT BEVERAGES"
      }
    ]
    
    Important: Use ONLY the text provided to extract information. Never include fake or additional menu items that aren't in the text.
    For price, include only the numeric value without currency symbols.
    
    Text: {text}
    
    Return only valid JSON array, no additional text.
    """
    
    try:
        response = text_model.invoke(prompt.format(text=menu_text))
        content = response.content.strip()
        
        # Clean response and parse JSON
        if '```json' in content:
            content = content.split('```json')[1]
        if '```' in content:
            content = content.split('```')[0]
            
        content = content.strip()
        logger.info(f"OCR response content (first 100 chars): {content[:100]}...")
        
        items = json.loads(content)
        if isinstance(items, list):
            logger.info(f"Successfully parsed {len(items)} menu items from OCR text")
            return items
        return []
        
    except Exception as e:
        logger.error(f"Error parsing menu text: {str(e)}")
        logger.error(f"Failed JSON content (first 200 chars): {menu_text[:200]}...")
        return []

def parse_menu_image(image_data: bytes) -> List[Dict[str, Any]]:
    """Parse menu image and extract menu items using vision model."""
    if not vision_model:
        return []
        
    try:
        image = Image.open(io.BytesIO(image_data))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            
        # Convert image back to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG')
        processed_image_data = img_buffer.getvalue()
        
        base64_image = encode_image(processed_image_data)
        
        prompt = """
        Analyze this menu image carefully and extract ALL menu items.

        Return a JSON array of objects with these fields:
        - name (required): item name (e.g., "Café Americano", "Hot Chocolate")
        - price (required): numeric price only (just the number, no currency symbols)
        - description (optional): full item description
        - category (optional): menu section/category name (e.g., "COFFEES", "HOT BEVERAGES") 
        - size (optional): size information if mentioned
        
        Example output format:
        [
          {
            "name": "Café Americano",
            "description": "Black Coffee",
            "price": 90,
            "category": "COFFEES"
          },
          {
            "name": "Hot Chocolate",
            "description": "Hershey's Cocoa Syrup Mixed With Warm Steamed Milk",
            "price": 130,
            "category": "HOT BEVERAGES"
          }
        ]
        
        Important: Extract EVERY menu item visible in the image with its correct price.
        Include items from ALL categories/sections.
        Return only valid JSON array, no additional text.
        """
        
        # Create message with image
        message_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
        
        response = vision_model.invoke([{"role": "user", "content": message_content}])
        content = response.content.strip()
        
        # Clean and parse JSON response
        if '```json' in content:
            content = content.split('```json')[1]
        if '```' in content:
            content = content.split('```')[0]

        content = content.strip()
        logger.info(f"Vision response content (first 100 chars): {content[:100]}...")
        
        items = json.loads(content)
        if isinstance(items, list):
            logger.info(f"Successfully parsed {len(items)} menu items from image")
            return items
        return []
        
    except Exception as e:
        logger.error(f"Error parsing menu image: {str(e)}")
        # Add more debug information
        if 'content' in locals():
            logger.error(f"Failed JSON content (first 200 chars): {content[:200]}...")
        return []

def merge_menu_items(vision_items: List[Dict[str, Any]], ocr_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge menu items from vision and OCR extractions, removing duplicates."""
    if not vision_items and not ocr_items:
        return []
    if not vision_items:
        return ocr_items or []
    if not ocr_items:
        return vision_items or []
    
    # Create a key function to identify unique items based on name and size (if available)
    def item_key(item):
        name = item.get('name', '').lower()
        size = item.get('size', '').lower()
        return f"{name}__{size}" if size else name
    
    # Start with vision items
    merged_items = vision_items.copy()
    vision_item_keys = {item_key(item) for item in vision_items if item.get("name")}
    
    # Add unique OCR items
    for ocr_item in ocr_items:
        if not ocr_item.get("name"):
            continue
            
        if item_key(ocr_item) not in vision_item_keys:
            merged_items.append(ocr_item)
            vision_item_keys.add(item_key(ocr_item))
    
    logger.info(f"Merged menu items: {len(vision_items)} vision + {len(ocr_items)} OCR = {len(merged_items)} total")
    return merged_items