from typing import List, Dict, Tuple, Optional
from app.config import logger
from difflib import SequenceMatcher

def string_similarity(a, b):
    """Calculate similarity ratio between two strings."""
    if not a or not b:
        return 0
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def merge_menu_items(vision_items: List[Dict], ocr_items: List[Dict]) -> List[Dict]:
    """Merge results from vision API and OCR+LLM approach."""
    # Validate inputs to prevent None errors
    if vision_items is None:
        vision_items = []
    if ocr_items is None:
        ocr_items = []
        
    # Log the items we're working with
    logger.info(f"Merging {len(vision_items)} vision items with {len(ocr_items)} OCR items")
    
    # Start with vision items as the base
    merged_items = vision_items.copy() if vision_items else []
    
    # If no vision items, fall back to OCR items
    if not merged_items and ocr_items:
        return ocr_items
        
    # If we have both, try to enhance vision items with OCR data
    if ocr_items and vision_items:
        # For each OCR item, check if it exists in vision items
        for ocr_item in ocr_items:
            if not ocr_item:
                logger.warning("Found None item in OCR items, skipping")
                continue
                
            # Check if name exists and is not None before calling strip()
            ocr_name = ocr_item.get("name", "")
            if ocr_name is None:
                logger.warning(f"OCR item has None name, using empty string instead: {ocr_item}")
                ocr_name = ""
            else:
                ocr_name = ocr_name.strip()
                
            if not ocr_name:
                logger.warning(f"Skipping OCR item with empty name: {ocr_item}")
                continue
                
            # Find best matching item in vision results
            best_match = None
            best_score = 0
            
            for i, vision_item in enumerate(merged_items):
                if not vision_item:
                    continue
                    
                # Check if name exists and is not None
                vision_name = vision_item.get("name", "")
                if vision_name is None:
                    vision_name = ""
                else:
                    vision_name = vision_name.strip()
                    
                if not vision_name:
                    continue
                    
                similarity = string_similarity(ocr_name, vision_name)
                if similarity > 0.8 and similarity > best_score:  # 80% similarity threshold
                    best_score = similarity
                    best_match = i
            
            # If found a match, use OCR data to fill in missing fields
            if best_match is not None:
                for field in ["description", "price", "category"]:
                    if (not merged_items[best_match].get(field) or merged_items[best_match].get(field) is None) and ocr_item.get(field):
                        merged_items[best_match][field] = ocr_item.get(field)
            else:
                # If no match found, this might be a missed item, add it
                merged_items.append(ocr_item)
    
    # Remove any items without both name and price
    valid_items = []
    for item in merged_items:
        if not item:
            continue
            
        # Ensure item has name
        name = item.get("name")
        if name is None or not str(name).strip():
            continue
            
        # Ensure item has price
        if item.get("price") is not None:
            # Ensure price is a number
            try:
                item["price"] = float(item["price"])
                valid_items.append(item)
            except (ValueError, TypeError):
                # Try to convert string price format (e.g. "90/-")
                price_str = str(item["price"]).strip()
                if price_str.endswith("/-"):
                    price_str = price_str[:-2]
                try:
                    item["price"] = float(price_str)
                    valid_items.append(item)
                except (ValueError, TypeError):
                    # Skip items with invalid prices
                    logger.warning(f"Skipping item with invalid price: {item}")
                    continue
        else:
            logger.warning(f"Skipping item without price: {item}")
    
    logger.info(f"Merged items count after validation: {len(valid_items)}")
    return valid_items

def map_to_menu_items(restaurant_id: str, items: List[Dict]) -> List[Dict]:
    """Map parsed items to the menu item schema."""
    menu_items = []
    
    if not items:
        logger.warning("No items to map to menu items")
        return []
    
    for item in items:
        if not item:
            continue
            
        # Build name - ensure it's not None
        name = item.get("name")
        if name is None:
            continue
        name = str(name).strip()
        if not name:
            continue
            
        # Build description with category if available - ensure it's not None
        description = item.get("description")
        if description is None:
            description = ""
        else:
            description = str(description)
            
        # Add category to description if available
        category = item.get("category")
        if category and "category" not in description.lower():
            category_prefix = f"Category: {category}"
            description = f"{category_prefix}\n{description}".strip()
            
        # Format price properly
        price = 0
        try:
            price_raw = item.get("price", 0)
            price = float(price_raw)
        except (ValueError, TypeError):
            # Try to extract number from string like "90/-"
            price_str = str(price_raw).strip()
            if price_str.endswith("/-"):
                price_str = price_str[:-2]
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                price = 0
                
        menu_item = {
            "restaurant_id": restaurant_id,
            "name": name,
            "description": description,
            "price": price,
            "is_active": True
        }
        menu_items.append(menu_item)
        
    return menu_items

def validate_menu_items(menu_items: List[Dict]) -> Tuple[bool, Optional[str]]:
    """Verify menu items before sending to API."""
    if not menu_items:
        return False, "No menu items to process"
    
    for i, item in enumerate(menu_items):
        if not item:
            return False, f"Item at position {i} is None"
            
        if not item.get("name"):
            return False, f"Item at position {i} has no name"
        
        if not item.get("restaurant_id"):
            return False, f"Item '{item.get('name')}' has no restaurant_id"
        
        try:
            price = float(item.get("price", 0))
            if price < 0:
                return False, f"Item '{item.get('name')}' has invalid price: {price}"
        except (ValueError, TypeError):
            return False, f"Item '{item.get('name')}' has non-numeric price: {item.get('price')}"

    return True, None