import io
import pytesseract
from PIL import Image
from app.config import logger

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Adjust path as needed

def extract_text(image_data: bytes) -> str:
    """Extract text from image using Tesseract OCR."""
    try:
        # Ensure we're working with bytes, not encoded strings
        if isinstance(image_data, str):
            logger.error("Image data is a string, not bytes. This is incorrect.")
            return ""
        
        # Validate image data
        if len(image_data) < 100:  # Very small files are suspicious
            logger.error(f"Image data is suspiciously small: {len(image_data)} bytes")
            return ""
            
        # Open and process the image
        try:
            image = Image.open(io.BytesIO(image_data))
            # Log image details
            logger.info(f"Image opened successfully. Size: {image.size}, Mode: {image.mode}")
        except Exception as img_err:
            logger.error(f"Failed to open image: {str(img_err)}")
            return ""
        
        # Improve OCR accuracy with preprocessing if needed
        image = image.convert('L')  # Convert to grayscale
        
        text = pytesseract.image_to_string(image)
        
        # Save OCR text to file for debugging
        with open("ocr_debug_output.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        logger.info(f"OCR extracted {len(text)} characters")
        
        # Log the first 100 characters to verify content
        if text:
            preview = text[:100].replace('\n', ' ')
            logger.info(f"OCR preview: {preview}...")
        else:
            logger.warning("OCR extracted empty text")
            
        return text
    except Exception as e:
        logger.error(f"Error during OCR extraction: {str(e)}")
        return ""