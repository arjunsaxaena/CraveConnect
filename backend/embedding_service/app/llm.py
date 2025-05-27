import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.messages import AIMessage
from typing import List, Dict, Any
import base64
from PIL import Image
import io
import json
from backend.data_pipeline_service.app.config import logger, GEMINI_API_KEY, LLM_MODEL, TEXT_MODEL

# Set up Google API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the models
vision_model = None
text_model = None
try:
    if GEMINI_API_KEY:
        # For gemini-1.5-flash, we can use the same model for both text and vision
        vision_model = ChatGoogleGenerativeAI(
            model=LLM_MODEL, 
            google_api_key=GEMINI_API_KEY,
            convert_system_message_to_human=True,
            credentials=None  # Explicitly disable ADC
        )
        text_model = ChatGoogleGenerativeAI(
            model=TEXT_MODEL, 
            google_api_key=GEMINI_API_KEY,
            convert_system_message_to_human=True,
            credentials=None  # Explicitly disable ADC
        )
        logger.info(f"LLM models initialized: {LLM_MODEL} for both text and vision")
    else:
        logger.warning("No Gemini API key provided. LLM functionality will be disabled.")
except Exception as e:
    logger.error(f"Error initializing LLM models: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

def encode_image(image_data: bytes) -> str:
    """Encode image data as base64 string."""
    return base64.b64encode(image_data).decode('utf-8')

def parse_menu_text(menu_text: str) -> List[Dict[str, Any]]:
    """
    Parse menu text using LangChain and Gemini model.
    
    Returns:
        List of dictionaries representing menu items
    """
    try:
        if not text_model:
            logger.warning("Text model not initialized. Cannot parse menu text.")
            return []
            
        system_message = SystemMessage(
            content="""You are an expert at extracting menu items from text. 
            Extract ALL menu items with their names, prices, sizes, and categories if available.
            
            For each menu item, extract:
            1. Name (required)
            2. Price in numeric format (required)
            3. Size (if applicable, e.g. "Small", "Medium", "Large")
            4. Description (optional)
            
            If multiple sizes are available for the same item, create separate entries for each size.
            Format your response as a JSON array of menu items."""
        )
        
        user_message = HumanMessage(
            content=f"""Extract all menu items from the following text:
            
            {menu_text}
            
            Return ONLY a valid JSON array of menu items with name, price, size, description, and category fields.
            Example format:
            [
                {{
                    "name": "Margherita Pizza",
                    "price": 12.99,
                    "size": "Medium",
                    "description": "Classic cheese pizza with tomato sauce",
                    "category": "Pizza"
                }},
                {{
                    "name": "Margherita Pizza",
                    "price": 15.99,
                    "size": "Large",
                    "description": "Classic cheese pizza with tomato sauce",
                    "category": "Pizza"
                }},
                ...
            ]
            """
        )
        
        messages = [system_message, user_message]
        
        try:
            response = text_model.invoke(messages)
            
            # Extract JSON from the response
            response_text = response.content
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No valid JSON found in LLM response")
                return []
                
            json_str = response_text[json_start:json_end]
            
            try:
                menu_items = json.loads(json_str)
                logger.info(f"Successfully parsed {len(menu_items)} menu items from text")
                return menu_items
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                return []
        except Exception as e:
            logger.error(f"Error invoking text model: {str(e)}")
            return []
            
    except Exception as e:
        logger.error(f"Error parsing menu text: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def parse_menu_image(image_data: bytes) -> List[Dict[str, Any]]:
    """
    Parse menu items directly from an image using LangChain and Gemini model.
    
    Returns:
        List of dictionaries representing menu items
    """
    try:
        if not vision_model:
            logger.warning("Vision model not initialized. Cannot parse menu image.")
            return []
            
        # Prepare the image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if image is in RGBA mode
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            
        # Resize if image is too large
        max_size = (1024, 1024)
        if image.width > max_size[0] or image.height > max_size[1]:
            image.thumbnail(max_size)
            
        # Convert back to bytes
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        processed_image_data = buffer.getvalue()
        
        system_message = SystemMessage(
            content="""You are an expert at extracting menu items from restaurant menu images.
            Extract ALL menu items with their names, prices, sizes, and categories if available.
            
            For each menu item, extract:
            1. Name (required)
            2. Price in numeric format (required, remove currency symbols)
            3. Size (if applicable, e.g. "Small", "Medium", "Large")
            4. Description (optional)
            5. Category (optional)
            
            If multiple sizes are available for the same item, create separate entries for each size.
            Format your response as a JSON array of menu items."""
        )
        
        # Base64 encode the image for the API
        image_b64 = encode_image(processed_image_data)
        
        user_message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": """Extract all menu items from this menu image.
                    Return ONLY a valid JSON array of menu items with name, price, size, description, and category fields.
                    Example format:
                    [
                        {
                            "name": "Margherita Pizza",
                            "price": 12.99,
                            "size": "Medium",
                            "description": "Classic cheese pizza with tomato sauce",
                            "category": "Pizza"
                        },
                        {
                            "name": "Margherita Pizza",
                            "price": 15.99,
                            "size": "Large",
                            "description": "Classic cheese pizza with tomato sauce",
                            "category": "Pizza"
                        },
                        ...
                    ]
                    """
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_b64}"
                }
            ]
        )
        
        messages = [system_message, user_message]
        
        try:
            response = vision_model.invoke(messages)
            
            # Extract JSON from the response
            response_text = response.content
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No valid JSON found in vision LLM response")
                return []
                
            json_str = response_text[json_start:json_end]
            
            try:
                menu_items = json.loads(json_str)
                logger.info(f"Successfully parsed {len(menu_items)} menu items from image")
                return menu_items
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error from image: {str(e)}")
                return []
        except Exception as e:
            logger.error(f"Error invoking vision model: {str(e)}")
            return []
            
    except Exception as e:
        logger.error(f"Error parsing menu image: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def merge_menu_items(vision_items: List[Dict[str, Any]], ocr_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge menu items from vision and OCR extractions, removing duplicates.
    
    Returns:
        Merged list of menu items
    """
    if not vision_items and not ocr_items:
        return []
        
    if not vision_items:
        return ocr_items
        
    if not ocr_items:
        return vision_items
        
    # Create a set of item names to check for duplicates
    merged_items = vision_items.copy()
    vision_item_names = {item["name"].lower() for item in vision_items if item.get("name")}
    
    # Add OCR items if they're not duplicates
    for ocr_item in ocr_items:
        if not ocr_item.get("name"):
            continue
            
        if ocr_item["name"].lower() not in vision_item_names:
            merged_items.append(ocr_item)
            vision_item_names.add(ocr_item["name"].lower())
    
    logger.info(f"Merged menu items: {len(vision_items)} vision + {len(ocr_items)} OCR = {len(merged_items)} total")
    return merged_items 