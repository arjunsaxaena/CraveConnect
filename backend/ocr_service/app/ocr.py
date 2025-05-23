import io
import cv2
import numpy as np
import pytesseract
from PIL import Image
from app.config import logger

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Adjust path as needed

def preprocess_image(image):
    """Apply preprocessing to improve OCR accuracy."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding to handle menu's dark background
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Optional: Noise reduction
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    return denoised

def analyze_image_quality(image):
    """Analyze image to determine quality metrics for OCR."""
    metrics = {}
    
    # Calculate contrast
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    metrics["contrast"] = gray.std()
    
    # Calculate brightness
    metrics["brightness"] = np.mean(gray)
    
    # Calculate sharpness
    laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
    metrics["sharpness"] = laplacian
    
    # Text regions estimation (approximate)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    metrics["text_area_ratio"] = np.sum(thresh) / (thresh.shape[0] * thresh.shape[1] * 255)
    
    logger.info(f"Image quality metrics: {metrics}")
    return metrics

def extract_text(image_data: bytes) -> str:
    """Extract text from image using Tesseract OCR with improved preprocessing."""
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
            # Convert to OpenCV format for preprocessing
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Analyze image quality
            analyze_image_quality(img)
            
            # Apply preprocessing
            processed_img = preprocess_image(img)
            
            # Save processed image for debugging
            cv2.imwrite("debug_processed_image.jpg", processed_img)
            
            # Log image details
            logger.info(f"Image processed. Original size: {img.shape}")
        except Exception as img_err:
            logger.error(f"Failed to preprocess image: {str(img_err)}")
            return ""
        
        # OCR Configuration - optimize for menu text
        custom_config = r'--oem 3 --psm 6 -l eng'  # Assume English text
        
        # Apply OCR to processed image
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        
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