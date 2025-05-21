from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
import json
from typing import List, Dict
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="OCR Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro-vision')

# Menu service URL
MENU_SERVICE_URL = "http://localhost:8002/api/menu"

def extract_menu_items(image_data: bytes) -> List[Dict]:
    """Extract menu items and prices from image using Google's Generative AI."""
    try:
        # Create image part for the model
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": image_data
            }
        ]
        
        # Prompt for the model
        prompt = """
        Analyze this menu image and extract all menu items with their prices.
        Return the data in the following JSON format:
        {
            "items": [
                {
                    "name": "item name",
                    "description": "item description",
                    "price": price_value
                }
            ]
        }
        Only return the JSON, no other text.
        """
        
        # Generate response
        response = model.generate_content([prompt, image_parts])
        
        # Parse the response
        try:
            # Extract JSON from the response
            json_str = response.text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3]  # Remove ```json and ``` markers
            data = json.loads(json_str)
            return data.get("items", [])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return []
            
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return []

def create_menu_items(restaurant_id: str, items: List[Dict]) -> bool:
    """Create menu items in the menu service."""
    try:
        for item in items:
            menu_item = {
                "restaurant_id": restaurant_id,
                "name": item["name"],
                "description": item.get("description", ""),
                "price": float(item["price"]),
                "is_active": True
            }
            
            response = requests.post(
                MENU_SERVICE_URL,
                json=menu_item
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create menu item: {response.text}")
                return False
                
        return True
    except Exception as e:
        logger.error(f"Error creating menu items: {e}")
        return False

@app.post("/process-menu")
async def process_menu(
    restaurant_id: str,
    menu_image: UploadFile = File(...)
):
    """Process menu image and create menu items."""
    try:
        # Read image data
        image_data = await menu_image.read()
        
        # Extract menu items
        items = extract_menu_items(image_data)
        if not items:
            return {"error": "Failed to extract menu items"}
            
        # Create menu items
        success = create_menu_items(restaurant_id, items)
        if not success:
            return {"error": "Failed to create menu items"}
            
        return {
            "message": "Menu items processed successfully",
            "items": items
        }
        
    except Exception as e:
        logger.error(f"Error processing menu: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 