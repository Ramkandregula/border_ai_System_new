import os
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class InferenceEngine:
    """
    Unified inference engine for all ML models
    """

    def __init__(self, model_loader):
        self.model_loader = model_loader

    def detect_persons(
        self,
        image_path: str,
        confidence: float = 0.5
    ) -> Dict:
        """
        Detect persons using YOLOv8

        Args:
            image_path: Path to image
            confidence: Confidence threshold

        Returns:
            Detection results
        """
        try:
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": "Image file not found"
                }

            model = self.model_loader.get_model("detection")

            if model is None:
                return {
                    "success": False,
                    "error": "Detection model not loaded"
                }

            results = model(image_path, conf=confidence)

            detections = []
            track_counter = 0

            for result in results:
                for box in result.boxes:

                    # COCO person class
                    if int(box.cls) != 0:
                        continue

                    bbox = [
                        float(x)
                        for x in box.xyxy[0]
                    ]

                    x1, y1, x2, y2 = bbox

                    detections.append({
                        "track_id": track_counter,
                        "confidence": float(box.conf),
                        "bbox": bbox,
                        "area": (x2 - x1) * (y2 - y1),
                        "class": "person"
                    })

                    track_counter += 1

            return {
                "success": True,
                "image_path": image_path,
                "detections": detections,
                "persons_detected": len(detections),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.exception(
                f"Detection inference failed: {e}"
            )

            return {
                "success": False,
                "error": str(e)
            }

    def extract_text(
        self,
        image_path: str
    ) -> Dict:
        """
        Extract text using OCR

        Args:
            image_path: Path to image

        Returns:
            OCR results
        """
        try:
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": "Image file not found"
                }

            model = self.model_loader.get_model("ocr")

            if model is None:
                return {
                    "success": False,
                    "error": "OCR model not loaded"
                }

            results = model.readtext(image_path)

            extracted_text = []
            confidences = []

            details = []

            for bbox, text, conf in results:
                extracted_text.append(text)
                confidences.append(float(conf))

                details.append({
                    "bbox": bbox,
                    "text": text,
                    "confidence": float(conf)
                })

            avg_confidence = (
                sum(confidences) / len(confidences)
                if confidences else 0.0
            )

            return {
                "success": True,
                "image_path": image_path,
                "text": " ".join(extracted_text),
                "confidence": avg_confidence,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.exception(
                f"OCR inference failed: {e}"
            )

            return {
                "success": False,
                "error": str(e)
            }
