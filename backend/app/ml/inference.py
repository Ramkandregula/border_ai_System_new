import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Inference engine for ML models"""
    
    def __init__(self, model_loader):
        """
        Initialize inference engine
        
        Args:
            model_loader: ModelLoader instance
        """
        self.model_loader = model_loader
    
    def detect_persons(self, image_path: str, confidence: float = 0.5) -> Dict:
        """
        Detect persons in image
        
        Args:
            image_path: Path to image
            confidence: Confidence threshold
            
        Returns:
            Detection results
        """
        try:
            model = self.model_loader.get_model("detection")
            if not model:
                return {"error": "Detection model not loaded"}
            
            results = model(image_path, conf=confidence)
            detections = []
            
            for result in results:
                for box in result.boxes:
                    if int(box.cls) == 0:  # Person class
                        detections.append({
                            "confidence": float(box.conf),
                            "bbox": [float(x) for x in box.xyxy[0]]
                        })
            
            return {
                "success": True,
                "detections": detections,
                "count": len(detections)
            }
        
        except Exception as e:
            logger.error(f"Error in detection inference: {str(e)}")
            return {"error": str(e)}
    
    def extract_text(self, image_path: str) -> Dict:
        """
        Extract text from image
        
        Args:
            image_path: Path to image
            
        Returns:
            Extracted text
        """
        try:
            model = self.model_loader.get_model("ocr")
            if not model:
                return {"error": "OCR model not loaded"}
            
            results = model.readtext(image_path)
            texts = [text for (_, text, _) in results]
            
            return {
                "success": True,
                "text": " ".join(texts),
                "details": results
            }
        
        except Exception as e:
            logger.error(f"Error in OCR inference: {str(e)}")
            return {"error": str(e)}
