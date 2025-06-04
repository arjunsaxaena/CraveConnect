import base64
import asyncio
from typing import Optional
import google.generativeai as genai
from app.config import logger, GEMINI_API_KEY
import mimetypes
from PIL import Image
import io

class OCRTool:
    def __init__(self, api_key: Optional[str] = None):
        self.vision_model = None
        logger.info("Initializing OCRTool")
        
        if not api_key:
            logger.error("No API key provided for OCRTool initialization")
            return
            
        try:
            logger.info("Configuring Gemini API")
            genai.configure(api_key=api_key)
            logger.info("Creating Gemini vision model")
            self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Successfully initialized Gemini vision model")
        except Exception as e:
            logger.error(f"Error initializing Gemini vision model: {str(e)}")
        
    def run(self, image_data: bytes) -> str:
        if not self.vision_model:
            logger.error("Vision model not initialized")
            return ""
            
        try:
            logger.info("Opening image for processing")
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Image format: {image.format}, mode: {image.mode}")
            
            if image.format != 'JPEG':
                logger.info("Converting image to JPEG format")
                if image.mode in ('RGBA', 'LA'):
                    logger.info("Converting RGBA/LA image to RGB")
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                elif image.mode != 'RGB':
                    logger.info(f"Converting {image.mode} image to RGB")
                    image = image.convert('RGB')
                
                logger.info("Saving image as JPEG")
                jpeg_buffer = io.BytesIO()
                image.save(jpeg_buffer, format='JPEG', quality=95)
                image_data = jpeg_buffer.getvalue()
            
            logger.info("Preparing image for Gemini API")
            image_parts = [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode('utf-8')
            }]
            
            prompt = "Extract and return all text content from this image of a menu. Only return the text content, nothing else."
            logger.info("Sending request to Gemini API")
            
            response = self.vision_model.generate_content(
                contents=[{"role": "user", "parts": [{"text": prompt}, *image_parts]}]
            )
            
            if response and response.text:
                raw_text = response.text
                logger.info(f"OCR extracted text length: {len(raw_text)} chars")
                return raw_text
            logger.warning("No text extracted from image")
            return ""
                
        except Exception as e:
            logger.error(f"Gemini OCR processing error: {str(e)}")
            return ""
            
    async def arun(self, image_data: bytes) -> str:
        return await asyncio.to_thread(self.run, image_data)

ocr_tool = None
try:
    logger.info("Initializing global OCR tool")
    ocr_tool = OCRTool(api_key=GEMINI_API_KEY)
    if ocr_tool.vision_model:
        logger.info("OCR tool initialized successfully")
    else:
        logger.error("OCR tool initialized but vision model is not available")
except Exception as e:
    logger.error(f"Error initializing OCR tool: {str(e)}")