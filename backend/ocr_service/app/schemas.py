from typing import List, Dict, Tuple, Optional
from app.config import logger
from difflib import SequenceMatcher

def string_similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def merge_menu_items(vision_items: List[Dict], ocr_items: List[Dict]) -> List[Dict]:
    if vision_items is None:
        vision_items = []
    if ocr_items is None:
        ocr_items = []
    
    merged_items = vision_items.copy() if vision_items else []
    
    if not merged_items and ocr_items:
        return ocr_items
        
    if ocr_items and vision_items:
        for ocr_item in ocr_items:
            if not ocr_item:
                logger.warning("Found None item in OCR items, skipping")
                continue
                
            ocr_name = ocr_item.get("name", "")
            if ocr_name is None:
                logger.warning(f"OCR item has None name, using empty string instead: {ocr_item}")
                ocr_name = ""
            else:
                ocr_name = ocr_name.strip()
                
            if not ocr_name:
                logger.warning(f"Skipping OCR item with empty name: {ocr_item}")
                continue
                
            best_match = None
            best_score = 0
            
            for i, vision_item in enumerate(merged_items):
                if not vision_item:
                    continue
                    
                vision_name = vision_item.get("name", "")
                if vision_name is None:
                    vision_name = ""
                else:
                    vision_name = vision_name.strip()
                    
                if not vision_name:
                    continue
                    
                similarity = string_similarity(ocr_name, vision_name)
                if similarity > 0.8 and similarity > best_score:
                    best_score = similarity
                    best_match = i
            
            if best_match is not None:
                for field in ["description", "price", "category"]:
                    if (not merged_items[best_match].get(field) or merged_items[best_match].get(field) is None) and ocr_item.get(field):
                        merged_items[best_match][field] = ocr_item.get(field)
            else:
                merged_items.append(ocr_item)
    
    valid_items = []
    for item in merged_items:
        if not item:
            continue
            
        name = item.get("name")
        if name is None or not str(name).strip():
            continue
            
        price_info = item.get("price")
        if price_info is not None:
            if isinstance(price_info, dict):
                valid_items.append(item)
            else:
                try:
                    price = float(price_info)
                    item["price"] = price
                    valid_items.append(item)
                except (ValueError, TypeError):
                    price_str = str(price_info).strip()
                    if price_str.endswith("/-"):
                        price_str = price_str[:-2]
                    try:
                        price = float(price_str)
                        item["price"] = price
                        valid_items.append(item)
                    except (ValueError, TypeError):
                        logger.warning(f"Skipping item with invalid price: {item}")
                        continue
        else:
            logger.warning(f"Skipping item without price: {item}")
    
    logger.info(f"Merged items count after validation: {len(valid_items)}")
    return valid_items

def map_to_menu_items(restaurant_id: str, items: List[Dict]) -> List[Dict]:
    menu_items = []
    
    if not items:
        logger.warning("No items to map to menu items")
        return []
    
    for item in items:
        if not item:
            continue
            
        name = item.get("name")
        if name is None:
            continue
        name = str(name).strip()
        if not name:
            continue
            
        description = item.get("description")
        if description is None:
            description = ""
        else:
            description = str(description)
            
        category = item.get("category")
        if category and "category" not in description.lower():
            category_prefix = f"Category: {category}"
            description = f"{category_prefix}\n{description}".strip()
            
        price_info = item.get("price", {})
        if isinstance(price_info, dict):
            for size, price in price_info.items():
                try:
                    price_value = float(price)
                    menu_item = {
                        "restaurant_id": restaurant_id,
                        "name": name,
                        "description": description,
                        "price": price_value,
                        "size": size.strip(),
                        "is_active": True
                    }
                    menu_items.append(menu_item)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid price for size {size}: {price}")
        else:
            try:
                price_raw = price_info
                price = float(price_raw)
                menu_item = {
                    "restaurant_id": restaurant_id,
                    "name": name,
                    "description": description,
                    "price": price,
                    "size": "",
                    "is_active": True
                }
                menu_items.append(menu_item)
            except (ValueError, TypeError):
                price_str = str(price_raw).strip()
                if price_str.endswith("/-"):
                    price_str = price_str[:-2]
                try:
                    price = float(price_str)
                    menu_item = {
                        "restaurant_id": restaurant_id,
                        "name": name,
                        "description": description,
                        "price": price,
                        "size": "",
                        "is_active": True
                    }
                    menu_items.append(menu_item)
                except (ValueError, TypeError):
                    logger.warning(f"Skipping item with invalid price: {item}")
                    continue
        
    return menu_items

def validate_menu_items(menu_items: List[Dict]) -> Tuple[bool, Optional[str]]:
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
        
        size = item.get("size")
        if size is not None and not isinstance(size, str):
            return False, f"Item '{item.get('name')}' has invalid size type: {type(size)}"

    return True, None