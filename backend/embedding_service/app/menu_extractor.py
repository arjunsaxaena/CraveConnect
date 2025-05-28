import re
import json
import asyncio
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.config import logger, GEMINI_API_KEY, LLM_MODEL
from app.menu_analyzer import menu_analyzer
from app.post_processor import MenuItemPostProcessor

class MenuItemExtractor:
    """Universal menu item extractor that adapts to any menu format."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        self.model = None
        self.post_processor = MenuItemPostProcessor()
        
        if api_key:
            try:
                self.model = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key
                )
            except Exception as e:
                logger.error(f"Error initializing menu extractor LLM: {str(e)}")
    
    async def extract_items(self, menu_text: str, restaurant_id: str) -> List[Dict[str, Any]]:
        """Extract menu items using adaptive processing based on menu structure."""
        if not self.model or not menu_text.strip():
            return []
        
        try:
            # Analyze menu structure
            structure = menu_analyzer.analyze(menu_text)
            
            # Generate adaptive extraction prompt
            prompt = self._create_extraction_prompt(menu_text, structure)
            
            # Call LLM
            messages = [HumanMessage(content=prompt)]
            response = await asyncio.to_thread(self.model.generate, [messages])
            
            if not response.generations or not response.generations[0]:
                return []
                
            content = response.generations[0][0].text
            menu_items = self._extract_json_from_response(content)
            
            if not menu_items:
                return await self._fallback_extraction(menu_text, restaurant_id, structure)
            
            # Process and clean extracted items
            menu_items = self._process_items(menu_items, restaurant_id)
            menu_items = self.post_processor.process_items(menu_items, menu_text)
            
            # Validate extraction quality
            expected_count = self._estimate_item_count(menu_text, structure)
            if len(menu_items) < expected_count * 0.5:
                fallback_items = await self._fallback_extraction(menu_text, restaurant_id, structure)
                fallback_items = self._process_items(fallback_items, restaurant_id) 
                fallback_items = self.post_processor.process_items(fallback_items, menu_text)
                
                # Use whichever extraction produced more items
                if len(fallback_items) > len(menu_items):
                    menu_items = fallback_items
            
            return menu_items
            
        except Exception as e:
            logger.error(f"Error extracting menu items: {str(e)}")
            return await self._fallback_extraction(menu_text, restaurant_id)
            
    def _process_items(self, items: List[Dict[str, Any]], restaurant_id: str) -> List[Dict[str, Any]]:
        """Process and clean extracted items."""
        processed_items = []
        
        for item in items:
            try:
                if not item or not item.get("name"):
                    continue
                    
                # Add restaurant ID
                item["restaurant_id"] = restaurant_id
                
                # Extract description from name if in parentheses and no description exists
                if "name" in item:
                    name = str(item["name"]).strip()
                    desc_match = re.search(r'\(([^)]+)\)$', name)
                    
                    if desc_match and (not item.get("description") or not item["description"].strip()):
                        parenthetical_text = desc_match.group(1).strip()
                        item["description"] = parenthetical_text
                    
                    item["name"] = re.sub(r'\s*\([^)]+\)$', '', name).strip()
                
                # Ensure description exists
                if "description" not in item or not item["description"]:
                    item["description"] = ""
                else:
                    item["description"] = str(item["description"]).strip()
                
                # Clean up price
                if "price" in item and item["price"]:
                    if isinstance(item["price"], str):
                        # Remove non-numeric characters
                        price_str = re.sub(r'[^\d.]', '', item["price"])
                        try:
                            item["price"] = float(price_str) if price_str else 0
                        except ValueError:
                            item["price"] = 0
                
                # Ensure size field exists
                if "size" not in item:
                    item["size"] = ""
                
                processed_items.append(item)
                
            except Exception as e:
                logger.error(f"Error processing item: {str(e)}")
                continue
                
        return processed_items
    
    def _create_extraction_prompt(self, menu_text: str, structure: Dict[str, Any]) -> str:
        """Create extraction prompt optimized for the specific menu structure."""
        price_format = structure["price_format"]["format"]
        
        prompt = """You are an expert menu item extractor. Extract ALL items from the following menu as a JSON array.

        For each item include:
        - name: ONLY the item name itself WITHOUT any description text in parentheses
        - description: Any descriptive text about the item (usually appears in parentheses after the name)
        - price: The item's price as a number (without currency symbols)
        - category: The menu section or category the item belongs to

        IMPORTANT NAME VS. DESCRIPTION SEPARATION:
        - The name field should contain ONLY the actual dish name (like 'Café Mocha')
        - If text appears in parentheses after the item name, put it in the description field, NOT in the name field

        OTHER IMPORTANT INSTRUCTIONS:
        - Extract EVERY menu item with its correct price
        - For items that come in multiple sizes, create a SEPARATE complete entry for EACH size with its specific price
        - Do not omit any items, even if they seem like add-ons or extras
        """
        
        price_guidance = "PRICE FORMAT: "
        if price_format == "with_slash":
            price_guidance += "Prices appear as numbers followed by '/- ' (e.g., '150/-'). Extract just the number."
        elif price_format == "with_decimal":
            price_guidance += "Prices appear as decimal numbers (e.g., '9.99'). Extract the full number."
        elif price_format == "with_currency":
            price_guidance += "Prices appear with currency symbols. Extract just the number without the symbol."
        else:
            price_guidance += "Prices appear as simple numbers. Extract them as-is."
            
        prompt += f"\n\n{price_guidance}\n\nMenu text:\n{menu_text}\n\n"
        prompt += "Format your response ONLY as a valid JSON array of objects. Include EVERY menu item."
        
        return prompt
        
    def _extract_json_from_response(self, llm_response: str) -> List[Dict[str, Any]]:
        """Extract JSON array from LLM response text."""
        try:
            # Find JSON array in response
            json_match = re.search(r'\[[\s\S]*\]', llm_response)
            if not json_match:
                logger.warning("No JSON array found in LLM response")
                return []
                
            json_str = json_match.group(0)
            items = json.loads(json_str)
            return items
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from LLM response: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error extracting JSON from response: {str(e)}")
            return []
    
    async def _fallback_extraction(self, menu_text: str, restaurant_id: str,
                                 structure: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fallback method for more aggressive menu item extraction."""
        if not self.model:
            return []
            
        try:
            #prompt with specific size instructions
            prompt = f"""
            EMERGENCY MENU EXTRACTION! Previous attempt didn't get all items.
            
            Extract EVERY menu item from this text as a JSON array:
            
            CRITICAL INSTRUCTIONS:
            1. Create a SEPARATE JSON object for EACH item on the menu
            2. If an item comes in multiple sizes, create MULTIPLE entries, one for EACH SIZE with its specific price
            3. For each item include: name, description, price (as number only), category
            4. Do NOT miss any items, including add-ons, extras, toppings, etc.
            5. Make sure EVERY item has the correct price
            
            Menu text:
            {menu_text}
            
            RESPONSE FORMAT: ONLY a valid JSON array with all menu items
            """
            
            # Call LLM
            messages = [HumanMessage(content=prompt)]
            response = await asyncio.to_thread(self.model.generate, [messages])
            
            if not response.generations or not response.generations[0]:
                return []
                
            content = response.generations[0][0].text
            
            # Extract JSON and return
            return self._extract_json_from_response(content)
            
        except Exception as e:
            logger.error(f"Error in fallback extraction: {str(e)}")
            return []
    
    def _estimate_item_count(self, menu_text: str, structure: Dict[str, Any]) -> int:
        """Estimate expected number of menu items."""
        lines = menu_text.split('\n')
        price_pattern = structure["price_format"]["pattern"]
        
        price_count = sum(1 for line in lines if re.search(price_pattern, line))
        
        # If we have size columns, we need to account for item repetition
        if structure["layout"]["has_size_columns"]:
            num_sizes = len(structure["layout"]["size_columns"])
            if num_sizes > 1:
                price_count = int(price_count * 0.7)

        return max(10, price_count)

menu_extractor = MenuItemExtractor(api_key=GEMINI_API_KEY, model_name=LLM_MODEL)