"""
OCR package for menu processing in CraveConnect.

This package provides functionality to:
1. Extract text from menu images using OCR
2. Parse the text into structured data using LLM
3. Validate and map data to database schema
4. Submit data to API endpoints
"""

from .menu_processor import process_menu_image

__all__ = ['process_menu_image']
