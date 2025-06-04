import json
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.config import logger, GEMINI_API_KEY, LLM_MODEL, MENU_SERVICE_URL

class MenuItemExtractor:
    """Menu item extractor using OCR+LLM approach with category creation."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        self.model = None
        if api_key:
            try:
                self.model = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key
                )
            except Exception as e:
                logger.error(f"Error initializing menu extractor LLM: {str(e)}")
    
    async def extract_and_create(self, menu_text: str, restaurant_id: str) -> List[Dict[str, Any]]:
        """Extract categories/items, create categories, then create menu items with correct category_id."""
        if not self.model or not menu_text.strip():
            return []
        try:
            # Step 1: Extract categories and items using LLM
            categories_and_items = await self._extract_categories_and_items(menu_text)
            categories = categories_and_items.get("categories", [])
            menu_items = categories_and_items.get("menu_items", [])
            if not menu_items:
                logger.error("No menu items extracted from LLM response")
                return []
            # Step 2: Create categories and get their IDs
            category_map = await self._create_categories(categories, restaurant_id)
            # Step 3: For each menu item, build request body and POST
            created_items = await self._create_menu_items(menu_items, restaurant_id, category_map)
            return created_items
        except Exception as e:
            logger.error(f"Error in menu extraction pipeline: {str(e)}")
            return []

    async def _extract_categories_and_items(self, menu_text: str) -> Dict[str, Any]:
        """Extract categories and menu items using LLM."""
        prompt = f"""Extract menu categories and items from this text. Return a JSON object with categories and menu_items.\n\nMenu text:\n{menu_text}\n\nExample format:\n{{\n    "categories": [\n        {{\n            "name": "Ice Blended"\n        }}\n    ],\n    "menu_items": [\n        {{\n            "name": "BRRRISTA",\n            "category": "Ice Blended",\n            "prices": {{\n                "regular": 87.5,\n                "large": 90.5\n            }},\n            "nutritional_info": {{\n                "calories": 169\n            }}\n        }}\n    ]\n}}\n\nRules:\n1. Extract ALL items from the menu\n2. Use a dict for sizes/prices if multiple sizes (e.g., \"prices\": {{\"regular\": 87.5, \"large\": 90.5}})\n3. Only include optional fields (description, ingredients, nutritional_info) if present in the menu\n4. Use \"category\" field to indicate which category an item belongs to\n5. Return ONLY the JSON object, no other text\n"""
        try:
            messages = [HumanMessage(content=prompt)]
            response = await asyncio.to_thread(self.model.generate, [messages])
            if not response.generations or not response.generations[0]:
                logger.error("No response from LLM")
                return {"categories": [], "menu_items": []}
            content = response.generations[0][0].text.strip()
            logger.info(f"Raw LLM Response: {content}")
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                logger.info(f"Extracted JSON: {json_str}")
                result = json.loads(json_str)
                if not result.get("menu_items"):
                    logger.error("No menu items in parsed JSON")
                else:
                    logger.info(f"Successfully extracted {len(result['menu_items'])} menu items")
                return result
            else:
                logger.error("No JSON found in LLM response")
                return {"categories": [], "menu_items": []}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            logger.error(f"Raw LLM response: {content}")
            return {"categories": [], "menu_items": []}
        except Exception as e:
            logger.error(f"Unexpected error in LLM extraction: {str(e)}")
            return {"categories": [], "menu_items": []}

    async def _create_categories(self, categories: List[Dict[str, Any]], restaurant_id: str) -> Dict[str, str]:
        """Create categories via API and return mapping of category names to IDs."""
        category_map = {}
        async with aiohttp.ClientSession() as session:
            for category in categories:
                try:
                    category_data = {
                        "restaurant_id": restaurant_id,
                        "name": category["name"]
                    }
                    if "description" in category and category["description"]:
                        category_data["description"] = category["description"]
                    
                    async with session.post(
                        f"{MENU_SERVICE_URL}/api/menu/categories",
                        json=category_data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            category_map[category["name"]] = result["id"]
                            logger.info(f"Created category: {category['name']} with ID: {result['id']}")
                        else:
                            error_text = await response.text()
                            logger.error(f"Failed to create category {category['name']}: {error_text}")
                except Exception as e:
                    logger.error(f"Error creating category {category['name']}: {str(e)}")
        return category_map

    async def _create_menu_items(self, items: List[Dict[str, Any]], restaurant_id: str, category_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create menu items via API, using category_id if available, and only including present optional fields."""
        created_items = []
        menu_items_to_create = []
        
        # First, prepare all menu items with their category IDs
        for item in items:
            try:
                if not item or not item.get("name"):
                    continue
                    
                menu_item_data = {
                    "restaurant_id": restaurant_id,
                    "name": item["name"],
                    "prices": item["prices"],
                    "is_spicy": item.get("is_spicy", False),
                    "is_vegetarian": item.get("is_vegetarian", False),
                    "is_available": item.get("is_available", True),
                    "popularity_score": item.get("popularity_score", 0.0)
                }
                
                # Set category_id if category is present and mapped
                category = item.get("category")
                if category and category in category_map:
                    menu_item_data["category_id"] = category_map[category]
                else:
                    menu_item_data["category_id"] = None
                    
                # Only include optional fields if present
                if "description" in item and item["description"]:
                    menu_item_data["description"] = item["description"]
                if "ingredients" in item and item["ingredients"]:
                    menu_item_data["ingredients"] = item["ingredients"]
                if "nutritional_info" in item and item["nutritional_info"]:
                    menu_item_data["nutritional_info"] = item["nutritional_info"]
                    
                menu_items_to_create.append(menu_item_data)
                
            except Exception as e:
                logger.error(f"Error preparing menu item {item.get('name', '')}: {str(e)}")
                continue
        
        # Then, create all menu items in one batch
        if menu_items_to_create:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{MENU_SERVICE_URL}/api/menu",
                        json={"restaurant_id": restaurant_id, "menu_items": menu_items_to_create}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            created_items.extend(result)
                            logger.info(f"Successfully created {len(menu_items_to_create)} menu items")
                        else:
                            error_text = await response.text()
                            logger.error(f"Failed to create menu items: {error_text}")
            except Exception as e:
                logger.error(f"Error creating menu items: {str(e)}")
                
        return created_items

menu_extractor = MenuItemExtractor(api_key=GEMINI_API_KEY, model_name=LLM_MODEL)