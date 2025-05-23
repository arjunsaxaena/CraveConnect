import io
import cv2
import numpy as np
import pytesseract
from PIL import Image
from app.config import logger

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    return denoised

def analyze_image_quality(image):
    metrics = {}
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    metrics["contrast"] = gray.std()
    
    metrics["brightness"] = np.mean(gray)
    
    laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
    metrics["sharpness"] = laplacian
    
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    metrics["text_area_ratio"] = np.sum(thresh) / (thresh.shape[0] * thresh.shape[1] * 255)
    
    logger.info(f"Image quality metrics: {metrics}")
    return metrics

def extract_text(image_data: bytes) -> str:
    try:
        if isinstance(image_data, str):
            logger.error("Image data is a string, not bytes. This is incorrect.")
            return ""
        
        if len(image_data) < 100:
            logger.error(f"Image data is suspiciously small: {len(image_data)} bytes")
            return ""
            
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            analyze_image_quality(img)
            
            processed_img = preprocess_image(img)
        except Exception as img_err:
            logger.error(f"Failed to preprocess image: {str(img_err)}")
            return ""
        
        custom_config = r'--oem 3 --psm 6 -l eng'
        
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        
        if text:
            preview = text[:100].replace('\n', ' ')
        else:
            logger.warning("OCR extracted empty text")
            
        return text
    except Exception as e:
        logger.error(f"Error during OCR extraction: {str(e)}")
        return ""