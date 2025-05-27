import io
import pytesseract
from PIL import Image
from langchain.tools import BaseTool
from langchain.tools.base import ToolException
from app.config import logger

class OCRTool(BaseTool):
    name: str = "menu_ocr_tool"
    description: str = "Extract text from menu images"
    
    def _run(self, image_data: bytes) -> str:
        """Extract text from an image using Tesseract OCR."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode == 'RGBA':
                image = image.convert('RGB')
                
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                logger.warning("OCR returned empty text")
                return ""
                
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            raise ToolException(f"OCR extraction failed: {str(e)}")
    
    async def _arun(self, image_data: bytes) -> str:
        """Async version of text extraction."""
        return self._run(image_data)

def extract_text(image_data: bytes) -> str:
    """Simple function to extract text from image data."""
    ocr_tool = OCRTool()
    return ocr_tool._run(image_data)