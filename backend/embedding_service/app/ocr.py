import pytesseract
from PIL import Image
import io
from backend.data_pipeline_service.app.config import logger
from langchain.tools import BaseTool
from langchain.tools.base import ToolException
from typing import Optional, Any

class OCRTool(BaseTool):
    name: str = "menu_ocr_tool"
    description: str = "Extract text from menu images"
    
    def _run(self, image_data: bytes) -> str:
        """Extract text from an image using Tesseract OCR."""
        try:
            logger.info("Starting OCR text extraction")
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if image is in RGBA mode
            if image.mode == 'RGBA':
                image = image.convert('RGB')
                
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            if not text or len(text.strip()) == 0:
                logger.warning("OCR returned empty text")
                return ""
                
            logger.info(f"OCR extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise ToolException(f"OCR extraction failed: {str(e)}")
    
    async def _arun(self, image_data: bytes) -> str:
        """Async version of text extraction."""
        return self._run(image_data)

def extract_text(image_data: bytes) -> Optional[str]:
    """Extract text from an image using the OCR tool."""
    try:
        ocr_tool = OCRTool()
        return ocr_tool._run(image_data)
    except Exception as e:
        logger.error(f"Error in OCR extraction: {str(e)}")
        return None 