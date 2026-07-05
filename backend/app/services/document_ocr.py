import logging
from typing import Dict, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class DocumentOCRService:
    """Service for document OCR and text extraction"""
    
    def __init__(self, engine: str = "tesseract"):
        """
        Initialize OCR service
        
        Args:
            engine: OCR engine to use ('tesseract' or 'easyocr')
        """
        self.engine = engine
        self.ocr_model = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize OCR engine"""
        try:
            if self.engine == "tesseract":
                import pytesseract
                self.pytesseract = pytesseract
                logger.info("Tesseract OCR engine initialized")
            elif self.engine == "easyocr":
                import easyocr
                self.ocr_model = easyocr.Reader(['en'])
                logger.info("EasyOCR engine initialized")
            else:
                raise ValueError(f"Unknown OCR engine: {self.engine}")
        except Exception as e:
            logger.error(f"Error initializing OCR engine: {str(e)}")
            raise
    
    def extract_text(self, image_path: str) -> Dict:
        """
        Extract text from document image
        
        Args:
            image_path: Path to document image
            
        Returns:
            Dictionary with extracted text and confidence
        """
        try:
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            if self.engine == "tesseract":
                return self._extract_tesseract(image_path)
            elif self.engine == "easyocr":
                return self._extract_easyocr(image_path)
        
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def _extract_tesseract(self, image_path: str) -> Dict:
        """Extract text using Tesseract"""
        try:
            from PIL import Image
            
            image = Image.open(image_path)
            text = self.pytesseract.image_to_string(image)
            
            # Get confidence
            data = self.pytesseract.image_to_data(image, output_type='dict')
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.info(f"Text extracted from {image_path}")
            
            return {
                "success": True,
                "image_path": image_path,
                "text": text.strip(),
                "confidence": avg_confidence / 100.0,  # Convert to 0-1 range
                "engine": "tesseract"
            }
        
        except Exception as e:
            logger.error(f"Tesseract extraction error: {str(e)}")
            raise
    
    def _extract_easyocr(self, image_path: str) -> Dict:
        """Extract text using EasyOCR"""
        try:
            results = self.ocr_model.readtext(image_path)
            
            texts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                texts.append(text)
                confidences.append(confidence)
            
            full_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.info(f"Text extracted from {image_path} using EasyOCR")
            
            return {
                "success": True,
                "image_path": image_path,
                "text": full_text,
                "confidence": avg_confidence,
                "engine": "easyocr",
                "details": results
            }
        
        except Exception as e:
            logger.error(f"EasyOCR extraction error: {str(e)}")
            raise
    
    def extract_fields(self, image_path: str) -> Dict:
        """
        Extract structured fields from document
        
        Args:
            image_path: Path to document image
            
        Returns:
            Dictionary with extracted fields
        """
        try:
            text_result = self.extract_text(image_path)
            if not text_result["success"]:
                return text_result
            
            text = text_result["text"]
            
            # Simple field extraction (can be enhanced with ML models)
            fields = {
                "name": self._extract_name(text),
                "date_of_birth": self._extract_date(text),
                "document_number": self._extract_document_number(text),
                "expiry_date": self._extract_expiry_date(text),
                "nationality": self._extract_nationality(text)
            }
            
            logger.info(f"Fields extracted from {image_path}")
            
            return {
                "success": True,
                "image_path": image_path,
                "fields": fields,
                "raw_text": text,
                "confidence": text_result["confidence"]
            }
        
        except Exception as e:
            logger.error(f"Error extracting fields: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fields": {}
            }
    
    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """Extract name from text"""
        # Simple extraction - can be enhanced
        lines = text.split('\n')
        for line in lines:
            if len(line.split()) >= 2 and line.isupper():
                return line.strip()
        return None
    
    @staticmethod
    def _extract_date(text: str) -> Optional[str]:
        """Extract date of birth"""
        import re
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        matches = re.findall(date_pattern, text)
        return matches[0] if matches else None
    
    @staticmethod
    def _extract_document_number(text: str) -> Optional[str]:
        """Extract document number"""
        import re
        # Pattern for passport/ID numbers
        pattern = r'[A-Z]{0,2}\d{6,9}'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    @staticmethod
    def _extract_expiry_date(text: str) -> Optional[str]:
        """Extract expiry date"""
        import re
        if "expiry" in text.lower() or "valid until" in text.lower():
            date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
            matches = re.findall(date_pattern, text)
            return matches[-1] if matches else None
        return None
    
    @staticmethod
    def _extract_nationality(text: str) -> Optional[str]:
        """Extract nationality"""
        # Simple extraction - can be enhanced
        countries = ["USA", "UK", "CANADA", "INDIA", "AUSTRALIA", "FRANCE", "GERMANY"]
        for country in countries:
            if country in text.upper():
                return country
        return None
