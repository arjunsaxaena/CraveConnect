"""
LLM Module for parsing menu text into structured data.
"""
import json
import logging
from typing import Dict, List, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

def gemini_parse_menu(raw_text: str, api_key: str) -> List[Dict[str, Any]]:
    if not api_key:
        raise ValueError("Gemini API key is required")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-pro')
        
        prompt = f"""
        You are a data extraction expert. Your task is to convert unstructured restaurant menu text (from OCR or scanned images) into structured data for a PostgreSQL database table called `MenuItems`. The table's schema is:

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
        
        # Generate LLM response
        response = model.generate_content(prompt)
        content = response.text
        
        # Extract and clean the JSON content
        if "```json" in content:
            json_content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_content = content.split("```")[1].strip()
        else:
            json_content = content.strip()
        
        # Parse and validate JSON
        menu_items = json.loads(json_content)
        logger.info(f"Successfully extracted {len(menu_items)} menu items")
        return menu_items
        
    except Exception as e:
        logger.error(f"LLM parsing failed: {e}")
        raise
