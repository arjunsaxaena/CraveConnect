import re
from typing import Dict, List, Any
from app.config import logger

class MenuStructureAnalyzer:
    def analyze(self, menu_text: str) -> Dict[str, Any]:
        sections = self._identify_sections(menu_text)
        price_format = self._detect_price_format(menu_text)
        layout = self._analyze_layout(menu_text)
        
        logger.info(f"Menu analysis: sections={len(sections)}, "
                   f"price_format={price_format['format']}, layout={layout['layout_type']}")
        
        return {
            "sections": sections,
            "price_format": price_format,
            "layout": layout
        }
    
    def _identify_sections(self, menu_text: str) -> List[Dict[str, Any]]:
        lines = menu_text.split('\n')
        sections = []
        current_section = None
        
        section_patterns = [
            r'^([A-Z][A-Z\s&\-:]+)$',
            r'^([A-Z][A-Za-z\s&\-]+)[\s]*:',
            r'^([^\w\s]*[A-Z][A-Za-z\s&\-]+[^\w\s]*)$'
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern, line):
                    if current_section:
                        sections.append(current_section)
                    
                    current_section = {
                        "name": line.strip(),
                        "start_line": i,
                        "end_line": None,
                        "content": []
                    }
                    is_header = True
                    break
            
            if not is_header and current_section:
                current_section["content"].append(line)
                current_section["end_line"] = i
        
        if current_section:
            sections.append(current_section)
        
        if not sections:
            sections = [{
                "name": "Menu Items",
                "start_line": 0,
                "end_line": len(lines) - 1,
                "content": [line.strip() for line in lines if line.strip()]
            }]
        
        return sections
    
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