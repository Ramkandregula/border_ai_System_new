import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)


class PersonDetectionService:
    """Service for person detection using YOLOv8"""
    
    def __init__(self, model_path: str = None, confidence_threshold: float = 0.5):
        """
        Initialize person detection service
        
        Args:
            model_path: Path to YOLOv8 model
            confidence_threshold: Confidence threshold for detections
        """
        self.model_path = model_path or "yolov8m.pt"
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize YOLOv8 model"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info(f"Person detection model loaded: {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading person detection model: {str(e)}")
            raise
    
    def detect_persons(self, image_path: str) -> Dict:
        """
        Detect persons in image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with detection results
        """
        try:
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Run inference
            results = self.model(image_path, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    if int(box.cls) == 0:  # Class 0 is 'person' in COCO
                        detection = {
                            "confidence": float(box.conf),
                            "bbox": [float(x) for x in box.xyxy[0]],  # x1, y1, x2, y2
                            "area": self._calculate_area(box.xyxy[0])
                        }
                        detections.append(detection)
            
            logger.info(f"Detected {len(detections)} persons in {image_path}")
            
            return {
                "success": True,
                "image_path": image_path,
                "persons_detected": len(detections),
                "detections": detections,
                "timestamp": self._get_timestamp()
            }
        
        except Exception as e:
            logger.error(f"Error detecting persons: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "persons_detected": 0,
                "detections": []
            }
    
    def detect_from_video(self, video_path: str, frame_skip: int = 1) -> Dict:
        """
        Detect persons in video
        
        Args:
            video_path: Path to video file
            frame_skip: Skip frames (1 = every frame, 2 = every 2nd frame, etc.)
            
        Returns:
            Dictionary with detection results
        """
        try:
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            detections_by_frame = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_skip == 0:
                    results = self.model(frame, conf=self.confidence_threshold)
                    
                    frame_detections = []
                    for result in results:
                        for box in result.boxes:
                            if int(box.cls) == 0:
                                detection = {
                                    "frame": frame_count,
                                    "confidence": float(box.conf),
                                    "bbox": [float(x) for x in box.xyxy[0]]
                                }
                                frame_detections.append(detection)
                    
                    if frame_detections:
                        detections_by_frame.append({
                            "frame": frame_count,
                            "detections": frame_detections
                        })
                
                frame_count += 1
            
            cap.release()
            
            logger.info(f"Video analysis complete: {frame_count} frames, {len(detections_by_frame)} frames with detections")
            
            return {
                "success": True,
                "video_path": video_path,
                "total_frames": frame_count,
                "frames_with_detections": len(detections_by_frame),
                "detections_by_frame": detections_by_frame[:100]  # Return first 100 frames
            }
        
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            cap.release()
            return {
                "success": False,
                "error": str(e),
                "detections_by_frame": []
            }
    
    @staticmethod
    def _calculate_area(bbox: List[float]) -> float:
        """Calculate bounding box area"""
        x1, y1, x2, y2 = bbox
        return float((x2 - x1) * (y2 - y1))
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
