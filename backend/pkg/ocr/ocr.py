"""
OCR Module for extracting text from menu images.
"""
import os
import logging
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

def ocr_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        logger.info(f"OCR extracted {len(text)} characters from image")
        return text
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise
