"""
Fine-tuning Script for YOLOv8 Detection Model
==============================================

This script fine-tunes a pre-trained YOLOv8 model on custom border
detection scenarios (e.g., crowded scenes, partial occlusion).

Dependencies:
    - ultralytics
    - opencv-python
    - torch
    - torchvision
    - pyyaml

Usage:
    python finetune_yolov8.py --data dataset.yaml --epochs 50 --batch 16 --device 0
    python finetune_yolov8.py --data dataset.yaml --model yolov8l --epochs 100 --batch 32
    python finetune_yolov8.py --data dataset.yaml --test path/to/test_image.jpg
    python finetune_yolov8.py --data dataset.yaml --export onnx
"""

import logging
import argparse
from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime
from ultralytics import YOLO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yolov8_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class YOLOv8Trainer:
    """Trainer for YOLOv8 model fine-tuning"""
    
    def __init__(self, model_name: str = 'yolov8m', device: Optional[int] = None):
        """
        Initialize YOLOv8 trainer
        
        Args:
            model_name: Model variant (nano, small, medium, large, xlarge)
            device: GPU device ID or None for auto
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.training_results = None
        
        try:
            logger.info(f"Loading YOLOv8 {model_name} model...")
            self.model = YOLO(f'{model_name}.pt')
            logger.info(f"Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def train(self, data_yaml: str, epochs: int = 50, batch_size: int = 16,
              imgsz: int = 640, patience: int = 20, **kwargs) -> Dict:
        """
        Fine-tune YOLOv8 model
        
        Args:
            data_yaml: Path to dataset YAML file
            epochs: Number of training epochs
            batch_size: Batch size
            imgsz: Image size
            patience: Early stopping patience
            **kwargs: Additional arguments for trainer
            
        Returns:
            Dictionary with training results
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting YOLOv8 {self.model_name} Fine-tuning")
            logger.info(f"{'='*60}")
            logger.info(f"Dataset: {data_yaml}")
            logger.info(f"Epochs: {epochs}")
            logger.info(f"Batch Size: {batch_size}")
            logger.info(f"Image Size: {imgsz}")
            logger.info(f"Patience: {patience}")
            
            # Train model
            results = self.model.train(
                data=data_yaml,
                epochs=epochs,
                imgsz=imgsz,
                batch=batch_size,
                device=self.device,
                patience=patience,
                save=True,
                plots=True,
                **kwargs
            )
            
            self.training_results = results
            logger.info(f"✅ Training completed successfully")
            
            return {
                'status': 'success',
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def validate(self, data_yaml: str, imgsz: int = 640) -> Dict:
        """
        Validate trained model
        
        Args:
            data_yaml: Path to dataset YAML file
            imgsz: Image size
            
        Returns:
            Dictionary with validation metrics
        """
        try:
            logger.info(f"\nValidating model...")
            
            results = self.model.val(data=data_yaml, imgsz=imgsz)
            
            logger.info(f"Validation Results:")
            logger.info(f"  mAP50: {results.box.map50:.4f}")
            logger.info(f"  mAP50-95: {results.box.map:.4f}")
            
            return {
                'status': 'success',
                'metrics': {
                    'map50': float(results.box.map50),
                    'map50_95': float(results.box.map)
                }
            }
        
        except Exception as e:
            logger.error(f"Error during validation: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def test(self, image_path: str, conf: float = 0.5) -> Dict:
        """
        Test model on single image
        
        Args:
            image_path: Path to test image
            conf: Confidence threshold
            
        Returns:
            Dictionary with detection results
        """
        try:
            logger.info(f"Testing model on: {image_path}")
            
            results = self.model.predict(image_path, conf=conf)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    if int(box.cls) == 0:  # Person class
                        detections.append({
                            'confidence': float(box.conf),
                            'bbox': [float(x) for x in box.xyxy[0]]
                        })
            
            logger.info(f"Detected {len(detections)} persons")
            
            return {
                'status': 'success',
                'detections': detections,
                'count': len(detections)
            }
        
        except Exception as e:
            logger.error(f"Error during testing: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def export_model(self, output_path: str, format: str = 'onnx') -> Dict:
        """
        Export model to different format
        
        Args:
            output_path: Output path
            format: Export format (onnx, torchscript, etc.)
            
        Returns:
            Dictionary with export status
        """
        try:
            logger.info(f"Exporting model to {format}...")
            
            exported_path = self.model.export(format=format, imgsz=640)
            
            logger.info(f"✅ Model exported to: {exported_path}")
            
            return {
                'status': 'success',
                'output_path': str(exported_path)
            }
        
        except Exception as e:
            logger.error(f"Error exporting model: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }


def create_dataset_yaml(dataset_path: str, output_yaml: str = 'dataset.yaml'):
    """
    Create dataset YAML configuration
    
    Args:
        dataset_path: Path to dataset directory
        output_yaml: Output YAML file path
    """
    try:
        import yaml
    except ImportError:
        logger.error("PyYAML not installed. Install with: pip install pyyaml")
        return
    
    dataset_config = {
        'path': str(Path(dataset_path).absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': 1,  # Number of classes (person)
        'names': {0: 'person'}
    }
    
    with open(output_yaml, 'w') as f:
        yaml.dump(dataset_config, f)
    
    logger.info(f"Dataset YAML created: {output_yaml}")


def main():
    """Main fine-tuning pipeline"""
    parser = argparse.ArgumentParser(description='Fine-tune YOLOv8 model')
    parser.add_argument('--data', type=str, required=True,
                       help='Path to dataset YAML')
    parser.add_argument('--model', type=str, default='yolov8m',
                       choices=['yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x'],
                       help='Model variant')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of epochs')
    parser.add_argument('--batch', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--device', type=int, default=0,
                       help='GPU device ID')
    parser.add_argument('--test', type=str,
                       help='Test image path')
    parser.add_argument('--export', type=str,
                       help='Export format (onnx, torchscript, etc.)')
    
    args = parser.parse_args()
    
    try:
        # Initialize trainer
        trainer = YOLOv8Trainer(model_name=args.model, device=args.device)
        
        # Train model
        train_results = trainer.train(
            data_yaml=args.data,
            epochs=args.epochs,
            batch_size=args.batch
        )
        
        if train_results['status'] == 'success':
            # Validate model
            val_results = trainer.validate(args.data)
            
            # Test on image if provided
            if args.test:
                test_results = trainer.test(args.test)
                logger.info(f"Test results: {test_results}")
            
            # Export model if format provided
            if args.export:
                export_results = trainer.export_model(
                    output_path=f'models/yolov8_{args.model}',
                    format=args.export
                )
                logger.info(f"Export results: {export_results}")
            
            logger.info(f"\n✅ Fine-tuning pipeline completed successfully!")
        else:
            logger.error(f"Training failed: {train_results}")
    
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
