from datetime import datetime
import uuid
import logging
from typing import Dict, List
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)


class PersonDetectionService:
    """Service for person detection using YOLOv8"""

    def __init__(
        self,
        model_path: str = None,
        confidence_threshold: float = 0.5
    ):
        self.model_path = model_path or "yolov8m.pt"
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize YOLOv8 model"""
        try:
            from ultralytics import YOLO

            self.model = YOLO(self.model_path)

            logger.info(
                f"Person detection model loaded: "
                f"{self.model_path}"
            )

        except Exception as e:
            logger.exception(
                f"Error loading detection model: {e}"
            )
            raise

    def detect_persons(self, image_path: str) -> Dict:
        """
        Detect persons in image
        """

        try:
            if not Path(image_path).exists():
                raise FileNotFoundError(
                    f"Image not found: {image_path}"
                )

            results = self.model(
                image_path,
                conf=self.confidence_threshold
            )

            detections = []
            track_counter = 0

            for result in results:

                for box in result.boxes:

                    # COCO class 0 = person
                    if int(box.cls) != 0:
                        continue

                    bbox = [
                        float(x)
                        for x in box.xyxy[0]
                    ]

                    detection = {
                        "detection_id":
                            str(uuid.uuid4()),

                        "track_id":
                            track_counter,

                        "class":
                            "person",

                        "confidence":
                            float(box.conf),

                        "bbox":
                            bbox,

                        "area":
                            self._calculate_area(
                                bbox
                            ),

                        "center":
                            [
                                (bbox[0]+bbox[2])/2,
                                (bbox[1]+bbox[3])/2
                            ]
                    }

                    detections.append(detection)
                    track_counter += 1

            logger.info(
                f"Detected "
                f"{len(detections)} persons"
            )

            return {
                "success": True,
                "image_path": image_path,
                "persons_detected":
                    len(detections),
                "detections":
                    detections,
                "model":
                    self.model_path,
                "timestamp":
                    self._get_timestamp()
            }

        except Exception as e:

            logger.exception(
                f"Detection error: {e}"
            )

            return {
                "success": False,
                "error": str(e),
                "persons_detected": 0,
                "detections": []
            }

    def detect_from_video(
        self,
        video_path: str,
        frame_skip: int = 1
    ) -> Dict:
        """
        Detect persons in video
        """

        cap = None

        try:
            if not Path(video_path).exists():
                raise FileNotFoundError(
                    f"Video not found: "
                    f"{video_path}"
                )

            cap = cv2.VideoCapture(
                video_path
            )

            fps = cap.get(
                cv2.CAP_PROP_FPS
            )

            frame_count = 0

            detections_by_frame = []

            while True:

                ret, frame = cap.read()

                if not ret:
                    break

                if (
                    frame_count %
                    frame_skip
                    == 0
                ):

                    results = self.model(
                        frame,
                        conf=self.confidence_threshold
                    )

                    frame_detections = []

                    for result in results:

                        for box in result.boxes:

                            if int(box.cls) != 0:
                                continue

                            bbox = [
                                float(x)
                                for x in box.xyxy[0]
                            ]

                            frame_detections.append({
                                "detection_id":
                                    str(
                                        uuid.uuid4()
                                    ),

                                "frame":
                                    frame_count,

                                "confidence":
                                    float(
                                        box.conf
                                    ),

                                "bbox":
                                    bbox,

                                "area":
                                    self._calculate_area(
                                        bbox
                                    )
                            })

                    if frame_detections:

                        detections_by_frame.append({
                            "frame":
                                frame_count,

                            "timestamp":
                                frame_count/fps
                                if fps
                                else 0,

                            "detections":
                                frame_detections
                        })

                frame_count += 1

            cap.release()

            logger.info(
                f"Processed "
                f"{frame_count} frames"
            )

            return {
                "success": True,
                "video_path":
                    video_path,
                "fps":
                    fps,
                "total_frames":
                    frame_count,
                "frames_with_detections":
                    len(
                        detections_by_frame
                    ),
                "detections_by_frame":
                    detections_by_frame[
                        :100
                    ],
                "timestamp":
                    self._get_timestamp()
            }

        except Exception as e:

            if cap:
                cap.release()

            logger.exception(
                f"Video analysis "
                f"error: {e}"
            )

            return {
                "success": False,
                "error": str(e),
                "detections_by_frame":
                    []
            }

    @staticmethod
    def _calculate_area(
        bbox: List[float]
    ) -> float:

        x1, y1, x2, y2 = bbox

        return float(
            (x2 - x1)
            * (y2 - y1)
        )

    @staticmethod
    def _get_timestamp():

        return (
            datetime
            .utcnow()
            .isoformat()
        )
