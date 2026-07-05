import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelLoader:
    """Loader for ML models"""
    
    def __init__(self, model_dir: str = "/app/models"):
        """
        Initialize model loader
        
        Args:
            model_dir: Directory containing models
        """
        self.model_dir = Path(model_dir)
        self.models = {}
    
    def load_detection_model(self) -> Optional[object]:
        """Load person detection model"""
        try:
            from ultralytics import YOLO
            model_path = self.model_dir / "yolov8m.pt"
            
            if not model_path.exists():
                logger.warning(f"Model not found: {model_path}")
                return None
            
            model = YOLO(str(model_path))
            self.models["detection"] = model
            logger.info("Detection model loaded")
            return model
        
        except Exception as e:
            logger.error(f"Error loading detection model: {str(e)}")
            return None
    
    def load_ocr_model(self) -> Optional[object]:
        """Load OCR model"""
        try:
            import easyocr
            model = easyocr.Reader(['en'])
            self.models["ocr"] = model
            logger.info("OCR model loaded")
            return model
        
        except Exception as e:
            logger.error(f"Error loading OCR model: {str(e)}")
            return None
    
    def get_model(self, model_name: str) -> Optional[object]:
        """Get loaded model"""
        return self.models.get(model_name)
