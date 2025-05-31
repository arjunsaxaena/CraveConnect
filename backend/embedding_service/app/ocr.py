"""Module for Optical Character Recognition (OCR) using Google's Gemini Vision API.

Defines OCRTool, which can be injected for testability and modularity.
"""

import base64
import asyncio
from typing import Optional
from functools import lru_cache

import google.generativeai as genai

from app.config import logger, settings


class OCRTool:
    """OCR tool for extracting text from images using Gemini Vision AI."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OCR tool with API key.

        Args:
            api_key: API key for Gemini Vision API
        """
        self.vision_model = None

        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini Vision model initialized successfully")
            except Exception as e:
                logger.error("Error initializing Gemini vision model: %s", str(e))

    async def extract_text(self, image_data: bytes) -> str:
        """Asynchronously extract text from image data.

        Args:
            image_data: Binary image data

        Returns:
            Extracted text from image
        """
        return await asyncio.to_thread(self._extract_text_sync, image_data)

    def _extract_text_sync(self, image_data: bytes) -> str:
        """Synchronously extract text from image data.

        Args:
            image_data: Binary image data

        Returns:
            Extracted text from image
        """
        if not self.vision_model:
            logger.warning("OCR tool not initialized")
            return ""

        try:
            image_parts = [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode('utf-8')
            }]

            prompt = ("Extract and return all text content from this image of a menu. "
                     "Only return the text content, nothing else.")

            response = self.vision_model.generate_content(
                contents=[{"role": "user", "parts": [{"text": prompt}, *image_parts]}]
            )

            if response and response.text:
                raw_text = response.text
                logger.info("OCR extracted text length: %s chars", len(raw_text))
                return raw_text

            logger.warning("OCR extraction returned empty response")
            return ""

        except Exception as e:
            logger.error("Gemini OCR processing error: %s", str(e))
            return ""


@lru_cache(maxsize=1)
def get_ocr_tool() -> Optional[OCRTool]:
    """Get OCR tool singleton instance.

    Returns:
        OCR tool instance or None if initialization fails
    """
    if not settings.ocr_enabled:
        logger.warning("OCR is disabled by configuration")
        return None

    if not settings.gemini_api_key:
        logger.error("Missing Gemini API key")
        return None

    try:
        return OCRTool(api_key=settings.gemini_api_key)
    except Exception as e:
        logger.error("Failed to initialize OCR tool: %s", str(e))
        return None


# Initialize OCR tool
ocr_tool = get_ocr_tool()
