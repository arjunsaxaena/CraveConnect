from sqlalchemy.orm import Session
from uuid import UUID
from PIL import Image
from app.repositories.repository import (
    MenuItemRepository,
    AddonsRepository,
    MenuItemAddonsRepository,
    RestaurantRepository,
)
from app.schemas.menu_items import MenuItemCreate, MenuItemOption
from app.schemas.addons import AddonsCreate
from app.schemas.menu_item_addons import MenuItemAddonsCreate
from app.core.errors import NotFoundError, BadRequestError
import logging
from app.core.config import settings
import google.generativeai as genai
import json
from app.models.filters import GetMenuItemFilters
from app.utils.embedding import create_menu_item_embedding

genai.configure(api_key=settings.GEMINI_API_KEY)

def extract_menu_data_from_image(file_path: str) -> dict:
    try:
        img = Image.open(file_path)
        
        prompt = """
        Analyze the menu image provided and extract all menu items and global addons.
        Return the data as a valid JSON object with two keys: "menu_items" and "global_addons".
        
        **CRITICAL INSTRUCTIONS:**
        1. First, scan the entire menu for:
           - Size legends or definitions (e.g., "S = Small (105 ML)", "R = Regular (165 ML)")
           - Global add-ons that apply to multiple items (e.g., extra toppings, extra cheese)
           - Pizza base upgrades or modifications (e.g., "Upgrade to Cheese Burst", "Make it C4 Cheezilicious")
           - Any sections starting with phrases like "Upgrade any pizza to", "Add extra", "Make it", "Convert to"
        
        2. **IMPORTANT**: The following should ALWAYS be categorized as global_addons, NOT menu items:
           - Any item prefixed with "Extra" (e.g., "Extra Cheese", "Extra Toppings")
           - Any item described as an upgrade or modification (e.g., "Upgrade to Cheese Burst")
           - Special pizza base variations (e.g., "C4 Cheezilicious", "Cheese Burst Base")
           - Additional toppings or ingredients that can be added
           - Any item that modifies or enhances an existing menu item
        
        3. **If a legend is found**, apply these definitions consistently across ALL extracted items.
        4. **If no legend is found**, use the option names exactly as they appear on the menu.
        5. **IMPORTANT**: For descriptions:
           - ALWAYS include any text in parentheses () or brackets [] after the item name as the description
           - Include any ingredient lists or preparation methods in the description
           - If multiple lines of description exist, combine them
           - If no explicit description is found, set to null

        The JSON structure should be:
        {
          "menu_items": [
            {
              "name": "Margherita Pizza",
              "description": "Classic tomato sauce and mozzarella",
              "price": 0,
              "options": [
                {"name": "Small", "price": 12.00},
                {"name": "Large", "price": 16.00}
              ],
              "addons": [],
              "tags": ["Vegetarian"],
              "allergens": ["Dairy"]
            }
          ],
          "global_addons": [
            {
              "name": "C4 Cheezilicious Upgrade",
              "description": "Upgrade any pizza to C4 Cheezilicious base",
              "options": [
                {"name": "Small", "price": 2.00},
                {"name": "Large", "price": 3.00}
              ]
            },
            {
              "name": "Cheese Burst Base",
              "description": "Convert to cheese burst pizza",
              "options": [
                {"name": "Small", "price": 1.50},
                {"name": "Large", "price": 2.50}
              ]
            },
            {
              "name": "Extra Toppings",
              "description": "Choice of: Onion/Capsicum/Sweet Corn/Jalapenos/Red Paprika/Mushroom",
              "options": [
                {"name": "Small", "price": 1.00},
                {"name": "Large", "price": 1.50}
              ]
            }
          ]
        }
        
        Remember:
        1. Menu items are ONLY standalone, orderable dishes (e.g., specific pizza types, drinks)
        2. Everything that modifies or upgrades an existing item goes in global_addons
        3. If you see phrases like "Upgrade to", "Convert to", "Make it" - those are ALWAYS addons
        4. Pizza base variations (Cheese Burst, C4 Cheezilicious, etc.) are ALWAYS addons
        5. Each addon should list its price options for different sizes if applicable
        6. ALWAYS include descriptions when they appear in the menu
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, img], stream=True)
        response.resolve()
        
        raw_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(raw_json)

    except Exception as e:
        logging.error(f"Error with Gemini API: {e}")
        raise BadRequestError(f"Failed to extract menu data from image: {e}")


def process_menu_image(db: Session, file_path: str, restaurant_id: UUID):
    menu_item_repo = MenuItemRepository()
    addon_repo = AddonsRepository()
    menu_item_addon_repo = MenuItemAddonsRepository()
    restaurant_repo = RestaurantRepository()

    restaurant = restaurant_repo.get(db, id=restaurant_id)
    if not restaurant:
        raise NotFoundError(f"Restaurant with id {restaurant_id} not found.")

    try:
        menu_data = extract_menu_data_from_image(file_path)

        for item_data in menu_data.get("menu_items", []):
            options_data = item_data.get("options", [])
            if not options_data and "price" in item_data:
                options_data = [{"name": "Regular", "price": item_data["price"]}]
            
            options = [
                MenuItemOption(
                    name=option["name"],
                    description=option.get("description"),
                    price=option["price"]
                ) for option in options_data
            ]

            menu_item_create = MenuItemCreate(
                restaurant_id=restaurant_id,
                name=item_data["name"],
                description=item_data.get("description", None),
                options=options,
                tags=item_data.get("tags", []),
                allergens=item_data.get("allergens", [])
            )
            menu_item = menu_item_repo.create(db, obj_in=menu_item_create)
            create_menu_item_embedding(db, menu_item.id, menu_item)

        for addon_data in menu_data.get("global_addons", []):
            addon_create = AddonsCreate(
                name=addon_data["name"],
                options=addon_data.get("options", [{"name": "Regular", "price": addon_data.get("price", 0)}])
            )
            addon = addon_repo.create(db, obj_in=addon_create)

            filters = GetMenuItemFilters(restaurant_id=restaurant_id)
            menu_items = menu_item_repo.get(db, filters=filters)
            for menu_item in menu_items:
                menu_item_addon_create = MenuItemAddonsCreate(
                    menu_item_id=menu_item.id,
                    addon_id=addon.id
                )
                menu_item_addon_repo.create(db, obj_in=menu_item_addon_create)

        logging.info(f"Successfully processed menu for restaurant {restaurant_id} from file {file_path}")
    except Exception as e:
        logging.error(f"Failed to process menu for restaurant {restaurant_id}: {e}")
        raise BadRequestError(f"Error processing menu file: {e}") 