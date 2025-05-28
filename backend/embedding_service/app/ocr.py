import base64
import asyncio
from typing import Optional
import google.generativeai as genai
from app.config import logger, GEMINI_API_KEY

class OCRTool:
    def __init__(self, api_key: Optional[str] = None):
        self.vision_model = None
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                logger.error(f"Error initializing Gemini vision model: {str(e)}")
        
    def run(self, image_data: bytes) -> str:
        if not self.vision_model:
            return ""
            
        try:
            image_parts = [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode('utf-8')
            }]
            
            prompt = "Extract and return all text content from this image of a menu. Only return the text content, nothing else."
            
            response = self.vision_model.generate_content(
                contents=[{"role": "user", "parts": [{"text": prompt}, *image_parts]}]
            )
            
            if response and response.text:
                raw_text = response.text
                logger.info(f"OCR extracted text length: {len(raw_text)} chars")
                return raw_text
            return ""
                
        except Exception as e:
            logger.error(f"Gemini OCR processing error: {str(e)}")
            return ""
            
    async def arun(self, image_data: bytes) -> str:
        return await asyncio.to_thread(self.run, image_data)

# Initialize OCR tool
ocr_tool = None
try:
    ocr_tool = OCRTool(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Error initializing OCR tool: {str(e)}")