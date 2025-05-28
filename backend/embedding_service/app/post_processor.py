import re
import json
from typing import List, Dict, Any
from app.config import logger

class MenuItemPostProcessor:
    def process_items(self, items: List[Dict[str, Any]], menu_text: str) -> List[Dict[str, Any]]:
        if not items:
            return []
        
        items = self._separate_name_description(items)
        base_name_groups = self._group_by_base_name(items)
        items = self._assign_sizes(items, base_name_groups, menu_text)
        return items
    
    def _separate_name_description(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for item in items:
            if not item.get("name"):
                continue
                
            name = item["name"]
            desc_match = re.search(r'\(([^)]+)\)$', name)
            if desc_match:
                extracted_desc = desc_match.group(1).strip()
                
                if not item.get("description") or not item["description"].strip():
                    item["description"] = extracted_desc
                    
                item["name"] = re.sub(r'\s*\([^)]+\)$', '', name).strip()
                
        return items
    
    def _group_by_base_name(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        groups = {}
        
        for item in items:
            if not item.get("name"):
                continue
                
            base_name = self._clean_item_name(item["name"])
            
            if base_name not in groups:
                groups[base_name] = []
                
            groups[base_name].append(item)
        
        return {name: items for name, items in groups.items() if len(items) > 1}
    
    def _clean_item_name(self, name: str) -> str:
        name = re.sub(r'\s*\([^)]*\)', '', name)
        name = re.sub(r'\b(small|medium|large|regular|half|full)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b[SML]\b', '', name)
        name = re.sub(r'\b\d+(\.\d+)?\s*(oz|inch|"|\'|cm)\b', '', name, flags=re.IGNORECASE)
        return name.strip()
    
    def _assign_sizes(self, items: List[Dict[str, Any]], groups: Dict[str, List[Dict[str, Any]]], 
                     menu_text: str) -> List[Dict[str, Any]]:
        if not groups:
            return items
            
        size_indicators = self._extract_size_indicators(menu_text)
        
        if size_indicators:
            logger.info(f"Found size indicators: {size_indicators}")
            
        for base_name, group_items in groups.items():
            group_items.sort(key=lambda x: x.get("price", 0))
            
            if size_indicators and len(group_items) <= len(size_indicators):
                for i, item in enumerate(group_items):
                    item["size"] = size_indicators[i]
            else:
                self._assign_generic_sizes(group_items)
        
        return items
    
    def _extract_size_indicators(self, menu_text: str) -> List[str]:
        size_indicators = []
        
        inch_pattern = re.compile(r'([SML])\s*(\d+)["\']', re.IGNORECASE)
        inch_matches = inch_pattern.findall(menu_text)
        if inch_matches and len(inch_matches) >= 2:
            return [f"{m[0]} {m[1]}\"" for m in inch_matches]
        
        inches_pattern = re.compile(r'(\d+)["\']', re.IGNORECASE)
        inch_numbers = inches_pattern.findall(menu_text)
        if inch_numbers and len(inch_numbers) >= 2:
            inch_numbers = [int(x) for x in inch_numbers if x.isdigit()]
            if inch_numbers and all(inch_numbers[i] < inch_numbers[i+1] for i in range(len(inch_numbers)-1)):
                return [f"{x}\"" for x in inch_numbers]
        
        size_words_pattern = re.compile(r'\b(Small|Medium|Large|Regular|Half|Full)\b', re.IGNORECASE)
        size_words = size_words_pattern.findall(menu_text)
        if size_words and len(set(size_words)) >= 2:
            size_map = {
                "small": "Small", "medium": "Medium", "large": "Large",
                "regular": "Regular", "half": "Half", "full": "Full"
            }
            
            seen = set()
            unique_sizes = [size_map.get(word.lower(), word) for word in size_words 
                           if not (word.lower() in seen or seen.add(word.lower()))]
            
            if len(unique_sizes) >= 2:
                return unique_sizes
        
        return []
    
    def _assign_generic_sizes(self, items: List[Dict[str, Any]]) -> None:
        if not items:
            return
            
        if len(items) == 2:
            size_names = ["Regular", "Large"]
        elif len(items) == 3:
            size_names = ["Small", "Medium", "Large"]
        else:
            size_names = ["Small", "Medium", "Large", "Extra Large", "Family", "Party"]
            while len(size_names) < len(items):
                size_names.append(f"Size {len(size_names) + 1}")
                
        for i, item in enumerate(items):
            if i < len(size_names):
                item["size"] = size_names[i]