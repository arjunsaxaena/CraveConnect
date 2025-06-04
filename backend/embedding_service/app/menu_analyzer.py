import re
from typing import Dict, List, Any
from app.config import logger
from app.ocr import ocr_tool

class MenuStructureAnalyzer:
    def analyze(self, menu_text: str) -> Dict[str, Any]:
        try:
            prompt = f"""Analyze this menu text and identify the main categories and their items. 
            Return the result in this exact JSON format:
            {{
                "categories": [
                    {{
                        "name": "Category Name",
                        "description": "Optional category description"
                    }}
                ],
                "menu_items": [
                    {{
                        "name": "Item Name",
                        "description": "Item Description",
                        "category_name": "Category this item belongs to",
                        "prices": {{
                            "S": price,
                            "R": price,
                            "L": price
                        }},
                        "is_spicy": false,
                        "is_vegetarian": false,
                        "is_available": true
                    }}
                ]
            }}

            Menu text:
            {menu_text}

            Important rules:
            1. Only identify main categories (e.g., Coffee, Smoothies, Ice Blended)
            2. Don't treat size indicators (S, R, L) as categories
            3. Group items under their main categories
            4. Extract prices for each size if available
            5. Include descriptions if present
            6. Set is_spicy and is_vegetarian based on item description
            """

            analysis = ocr_tool.vision_model.generate_content(prompt)
            structured_data = analysis.text
            
            import json
            menu_structure = json.loads(structured_data)
            
            sections = []
            for category in menu_structure["categories"]:
                section = {
                    "name": category["name"],
                    "description": category.get("description"),
                    "content": []
                }
                
                category_items = [
                    item for item in menu_structure["menu_items"]
                    if item["category_name"] == category["name"]
                ]
                
                for item in category_items:
                    item_text = item["name"]
                    if item["description"]:
                        item_text += f" ({item['description']})"
                    
                    prices = []
                    for size, price in item["prices"].items():
                        prices.append(f"{price}")
                    item_text += " " + " ".join(prices)
                    
                    section["content"].append(item_text)
                
                sections.append(section)
            
            price_format = self._detect_price_format(menu_text)
            layout = self._analyze_layout(menu_text)
            
            logger.info(f"Menu analysis: sections={len(sections)}, "
                       f"price_format={price_format['format']}, layout={layout['layout_type']}")
            
            return {
                "sections": sections,
                "price_format": price_format,
                "layout": layout,
                "menu_items": menu_structure["menu_items"]
            }
            
        except Exception as e:
            logger.error(f"Error in menu analysis: {str(e)}")
            return {
                "sections": [{
                    "name": "Menu Items",
                    "content": menu_text.split('\n')
                }],
                "price_format": self._detect_price_format(menu_text),
                "layout": self._analyze_layout(menu_text)
            }
    
    def _clean_section_name(self, name: str) -> str:
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        name = name.title()
        name = re.sub(r'[\d\s$₹€£\/\-\.]+$', '', name).strip()
        
        size_indicators = ['S', 'R', 'SR', 'L', 'M', 'Small', 'Regular', 'Large', 'Medium']
        if name.upper() in [s.upper() for s in size_indicators]:
            return ""
            
        return name
    
    def _is_valid_category(self, name: str) -> bool:
        if not name:
            return False
            
        size_indicators = ['S', 'R', 'SR', 'L', 'M', 'Small', 'Regular', 'Large', 'Medium']
        if name.upper() in [s.upper() for s in size_indicators]:
            return False
            
        if len(name) <= 2:
            return False
            
        if name.isdigit():
            return False
            
        return True
    
    def _detect_price_format(self, menu_text: str) -> Dict[str, Any]:
        price_formats = {
            "numeric_only": len(re.findall(r'(?<!\S)(\d+)(?!\d*\/)(?!\.\d)(?!\d)', menu_text)),
            "with_currency": len(re.findall(r'[$₹€£]\s*\d+', menu_text)),
            "with_slash": len(re.findall(r'\d+\s*\/-', menu_text)), 
            "with_decimal": len(re.findall(r'\d+\.\d+(?!\s*\/)', menu_text)),
            "with_decimal_slash": len(re.findall(r'\d+\.\d+\s*\/-', menu_text))
        }
        
        dominant_format = max(price_formats.items(), key=lambda x: x[1])
        
        pattern = None
        if dominant_format[0] == "with_slash":
            pattern = r'(\d+)\s*\/-'
        elif dominant_format[0] == "with_decimal_slash":
            pattern = r'(\d+\.\d+)\s*\/-'
        elif dominant_format[0] == "with_currency":
            pattern = r'[$₹€£]\s*(\d+(?:\.\d+)?)'
        elif dominant_format[0] == "with_decimal":
            pattern = r'(\d+\.\d+)'
        else:
            pattern = r'(?<!\S)(\d+)(?!\d*\/)(?!\.\d)(?!\d)'
        
        return {
            "format": dominant_format[0],
            "pattern": pattern
        }
    
    def _analyze_layout(self, menu_text: str) -> Dict[str, Any]:
        lines = menu_text.split('\n')
        result = {
            "layout_type": "standard",
            "has_descriptions": False,
            "has_size_columns": False,
            "size_columns": []
        }
        
        desc_matches = [re.search(r'\([^)]{5,}\)', line) for line in lines]
        desc_count = sum(1 for m in desc_matches if m)
        result["has_descriptions"] = desc_count > 2
        
        for i, line in enumerate(lines[:30]):
            size_pattern = re.compile(r'([SML]\s*\d+[\"\']|Small|Medium|Large|Regular|Half|Full)', re.IGNORECASE)
            matches = size_pattern.findall(line)
            
            if len(matches) >= 2:
                result["has_size_columns"] = True
                result["size_columns"] = matches
                result["layout_type"] = "size_column_layout"
                break
        
        return result

menu_analyzer = MenuStructureAnalyzer()