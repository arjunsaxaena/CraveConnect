from sqlalchemy.orm import Session
from uuid import UUID
from PIL import Image
from app.repositories.repository import (
    MenuItemRepository,
    MenuItemOptionsRepository,
    AddonsRepository,
    MenuItemAddonsRepository,
    RestaurantRepository,
)
from app.schemas.menu_items import MenuItemCreate
from app.schemas.menu_item_options import MenuItemOptionCreate
from app.schemas.addons import AddonsCreate
from app.schemas.menu_item_addons import MenuItemAddonsCreate
from app.core.errors import NotFoundError, BadRequestError
import logging
from app.core.config import settings
import google.generativeai as genai
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

def extract_menu_data_from_image(file_path: str) -> dict:
    try:
        img = Image.open(file_path)
        
        prompt = """
        Analyze the menu image provided and extract all menu items.
        Return the data as a valid JSON object with a single key: "menu_items".
        Each item in the "menu_items" list should have the following structure:
        - "name": The name of the menu item (e.g., "Margherita Pizza").
        - "description": A brief description, if available.
        - "price": The base price of the item. If the item has different sizes/options, set this to 0.
        - "options": A list of different sizes or choices for the item (e.g., "Small", "Medium", "Large"). Each option should have "name" and "price".
        - "addons": A list of extras that can be added (e.g., "Extra Cheese"). Each addon should include "name", "description", and "price".
        - "tags": A list of relevant tags (e.g., "Vegetarian", "Spicy").
        - "allergens": A list of potential allergens mentioned.
        
        Example for a pizza:
        {
          "name": "Classic Pepperoni",
          "description": "A classic pizza with pepperoni and mozzarella.",
          "price": 0,
          "options": [
            {"name": "Small", "price": 12.99},
            {"name": "Large", "price": 16.99}
          ],
          "addons": [
            {"name": "Extra Cheese", "description": "Add more cheese", "price": 2.50}
          ]
        }
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
    menu_item_option_repo = MenuItemOptionsRepository()
    addon_repo = AddonsRepository()
    menu_item_addon_repo = MenuItemAddonsRepository()
    restaurant_repo = RestaurantRepository()

    restaurant = restaurant_repo.get(db, id=restaurant_id)
    if not restaurant:
        raise NotFoundError(f"Restaurant with id {restaurant_id} not found.")

    try:
        menu_data = extract_menu_data_from_image(file_path)

        for item_data in menu_data.get("menu_items", []):
            menu_item_create = MenuItemCreate(
                restaurant_id=restaurant_id,
                name=item_data["name"],
                description=item_data.get("description"),
                price=item_data["price"],
                tags=item_data.get("tags"),
                allergens=item_data.get("allergens")
            )
            menu_item = menu_item_repo.create(db, obj_in=menu_item_create)

            for option_data in item_data.get("options", []):
                option_create = MenuItemOptionCreate(
                    menu_item_id=menu_item.id,
                    name=option_data["name"],
                    description=option_data.get("description"),
                    price=option_data["price"]
                )
                menu_item_option_repo.create(db, obj_in=option_create)

            for addon_data in item_data.get("addons", []):
                existing_addon = db.query(addon_repo.model).filter_by(name=addon_data["name"], price=addon_data["price"]).first()
                if existing_addon:
                    addon = existing_addon
                else:
                    addon_create = AddonsCreate(
                        name=addon_data["name"],
                        description=addon_data.get("description"),
                        price=addon_data["price"]
                    )
                    addon = addon_repo.create(db, obj_in=addon_create)
                
                menu_item_addon_create = MenuItemAddonsCreate(
                    menu_item_id=menu_item.id,
                    addon_id=addon.id
                )
                menu_item_addon_repo.create(db, obj_in=menu_item_addon_create)

        logging.info(f"Successfully processed menu for restaurant {restaurant_id} from file {file_path}")
    except Exception as e:
        logging.error(f"Failed to process menu for restaurant {restaurant_id}: {e}")
        raise BadRequestError(f"Error processing menu file: {e}") 