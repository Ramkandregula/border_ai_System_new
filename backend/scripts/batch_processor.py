"""
Batch Processing Pipeline for ML Models
========================================

This module implements efficient batch processing for detection and OCR
on large collections of images/videos with queue management and progress
tracking.

Dependencies:
    - opencv-python
    - torch
    - ultralytics
    - easyocr
    - tqdm
    - pillow

Usage:
    # Detection batch processing
    python batch_processor.py --input data/images --mode detection --batch-size 32 --output results/ --method threaded
    
    # OCR batch processing
    python batch_processor.py --input data/documents --mode ocr --workers 8 --output ocr_results/ --method multiprocess
    
    # Sequential processing (debugging)
    python batch_processor.py --input data/images --mode detection --method sequential
"""

import logging
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
import time

import numpy as np
import cv2
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """Base class for batch processing"""
    
    def __init__(self, batch_size: int = 32, num_workers: int = 4, 
                 output_dir: Optional[str] = None):
        """
        Initialize batch processor
        
        Args:
            batch_size: Batch size for processing
            num_workers: Number of worker threads/processes
            output_dir: Directory to save results
        """
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.output_dir = Path(output_dir) if output_dir else Path('results')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.total_processed = 0
        self.total_failed = 0
        self.results = []
        self.start_time = None
        
        logger.info(f"BatchProcessor initialized: workers={num_workers}, batch_size={batch_size}")
    
    def get_files(self, input_path: str, extensions: List[str] = None) -> List[str]:
        """
        Get list of files to process
        
        Args:
            input_path: Path to input directory
            extensions: File extensions to include
            
        Returns:
            List of file paths
        """
        input_dir = Path(input_path)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"Input path not found: {input_path}")
        
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.mp4', '.avi']
        
        files = []
        for ext in extensions:
            files.extend(input_dir.glob(f'**/*{ext}'))
            files.extend(input_dir.glob(f'**/*{ext.upper()}'))
        
        logger.info(f"Found {len(files)} files to process")
        return sorted(files)
    
    def process_batch(self, batch: List[str], process_func: Callable) -> List[Dict]:
        """
        Process a batch of files
        
        Args:
            batch: List of file paths
            process_func: Function to process each file
            
        Returns:
            List of results
        """
        results = []
        for file_path in batch:
            try:
                result = process_func(str(file_path))
                results.append({
                    'file': str(file_path),
                    'status': 'success',
                    'result': result
                })
                self.total_processed += 1
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                results.append({
                    'file': str(file_path),
                    'status': 'failed',
                    'error': str(e)
                })
                self.total_failed += 1
        
        return results
    
    def process_sequential(self, files: List[str], process_func: Callable) -> List[Dict]:
        """
        Process files sequentially (single-threaded)
        
        Args:
            files: List of file paths
            process_func: Processing function
            
        Returns:
            List of results
        """
        logger.info(f"Starting sequential processing of {len(files)} files...")
        
        results = []
        with tqdm(total=len(files), desc='Processing') as pbar:
            for file_path in files:
                try:
                    result = process_func(str(file_path))
                    results.append({
                        'file': str(file_path),
                        'status': 'success',
                        'result': result,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    self.total_processed += 1
                except Exception as e:
                    logger.error(f"Error: {str(e)}")
                    results.append({
                        'file': str(file_path),
                        'status': 'failed',
                        'error': str(e)
                    })
                    self.total_failed += 1
                
                pbar.update(1)
        
        return results
    
    def process_threaded(self, files: List[str], process_func: Callable) -> List[Dict]:
        """
        Process files using thread pool
        
        Args:
            files: List of file paths
            process_func: Processing function
            
        Returns:
            List of results
        """
        logger.info(f"Starting threaded processing with {self.num_workers} workers...")
        
        results = []
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(process_func, str(f)): f for f in files
            }
            
            with tqdm(total=len(files), desc='Processing') as pbar:
                for future in as_completed(futures):
                    file_path = futures[future]
                    try:
                        result = future.result(timeout=300)
                        results.append({
                            'file': str(file_path),
                            'status': 'success',
                            'result': result,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        self.total_processed += 1
                    except Exception as e:
                        logger.error(f"Error: {str(e)}")
                        results.append({
                            'file': str(file_path),
                            'status': 'failed',
                            'error': str(e)
                        })
                        self.total_failed += 1
                    
                    pbar.update(1)
        
        return results
    
    def process_multiprocess(self, files: List[str], process_func: Callable) -> List[Dict]:
        """
        Process files using process pool (better for CPU-bound tasks)
        
        Args:
            files: List of file paths
            process_func: Processing function
            
        Returns:
            List of results
        """
        logger.info(f"Starting multiprocess processing with {self.num_workers} workers...")
        
        results = []
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(process_func, str(f)): f for f in files
            }
            
            with tqdm(total=len(files), desc='Processing') as pbar:
                for future in as_completed(futures):
                    file_path = futures[future]
                    try:
                        result = future.result(timeout=600)
                        results.append({
                            'file': str(file_path),
                            'status': 'success',
                            'result': result,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        self.total_processed += 1
                    except Exception as e:
                        logger.error(f"Error: {str(e)}")
                        results.append({
                            'file': str(file_path),
                            'status': 'failed',
                            'error': str(e)
                        })
                        self.total_failed += 1
                    
                    pbar.update(1)
        
        return results
    
    def process_batched(self, files: List[str], process_func: Callable) -> List[Dict]:
        """
        Process files in batches
        
        Args:
            files: List of file paths
            process_func: Processing function
            
        Returns:
            List of results
        """
        logger.info(f"Starting batch processing (batch_size={self.batch_size})...")
        
        results = []
        batches = [files[i:i+self.batch_size] for i in range(0, len(files), self.batch_size)]
        
        for i, batch in enumerate(tqdm(batches, desc='Batches')):
            batch_results = self.process_batch(batch, process_func)
            results.extend(batch_results)
        
        return results
    
    def save_results(self, results: List[Dict], filename: str = 'results.json'):
        """
        Save results to JSON file
        
        Args:
            results: List of results
            filename: Output filename
        """
        output_path = self.output_dir / filename
        
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_files': len(results),
            'successful': self.total_processed,
            'failed': self.total_failed,
            'results': results
        }
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Results saved to {output_path}")
    
    def print_summary(self, elapsed_time: float):
        """Print processing summary"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Batch Processing Summary")
        logger.info(f"{'='*60}")
        logger.info(f"Total Processed: {self.total_processed}")
        logger.info(f"Total Failed:    {self.total_failed}")
        if self.total_processed + self.total_failed > 0:
            success_rate = self.total_processed / (self.total_processed + self.total_failed) * 100
            logger.info(f"Success Rate:    {success_rate:.1f}%")
        logger.info(f"Output Dir:      {self.output_dir}")
        logger.info(f"Total Time:      {elapsed_time:.2f} seconds")
        logger.info(f"{'='*60}")


class DetectionBatchProcessor(BatchProcessor):
    """Batch processor for object detection"""
    
    def __init__(self, model_path: str = 'yolov8m.pt', **kwargs):
        """
        Initialize detection batch processor
        
        Args:
            model_path: Path to YOLOv8 model
            **kwargs: Arguments for BatchProcessor
        """
        super().__init__(**kwargs)
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            logger.info(f"Detection model loaded: {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def detect_person(self, image_path: str, confidence: float = 0.5) -> Dict:
        """
        Detect persons in image
        
        Args:
            image_path: Path to image
            confidence: Confidence threshold
            
        Returns:
            Detection results
        """
        results = self.model(image_path, conf=confidence, verbose=False)
        
        detections = []
        for result in results:
            for box in result.boxes:
                if int(box.cls) == 0:  # Person class
                    detections.append({
                        'confidence': float(box.conf),
                        'bbox': [float(x) for x in box.xyxy[0]]
                    })
        
        return {
            'image': image_path,
            'persons_detected': len(detections),
            'detections': detections
        }


class OCRBatchProcessor(BatchProcessor):
    """Batch processor for OCR"""
    
    def __init__(self, engine: str = 'easyocr', **kwargs):
        """
        Initialize OCR batch processor
        
        Args:
            engine: OCR engine ('tesseract' or 'easyocr')
            **kwargs: Arguments for BatchProcessor
        """
        super().__init__(**kwargs)
        self.engine = engine
        
        if engine == 'easyocr':
            try:
                import easyocr
                self.ocr_model = easyocr.Reader(['en'])
                logger.info("EasyOCR model loaded")
            except Exception as e:
                logger.error(f"Error loading EasyOCR: {str(e)}")
                raise
        elif engine == 'tesseract':
            try:
                import pytesseract
                self.pytesseract = pytesseract
                logger.info("Tesseract OCR initialized")
            except Exception as e:
                logger.error(f"Error loading Tesseract: {str(e)}")
                raise
    
    def extract_text(self, image_path: str) -> Dict:
        """
        Extract text from image
        
        Args:
            image_path: Path to image
            
        Returns:
            Extracted text
        """
        if self.engine == 'easyocr':
            results = self.ocr_model.readtext(image_path)
            texts = [text for (_, text, _) in results]
            full_text = " ".join(texts)
            
            return {
                'image': image_path,
                'text': full_text,
                'engine': 'easyocr'
            }
        elif self.engine == 'tesseract':
            from PIL import Image
            image = Image.open(image_path)
            text = self.pytesseract.image_to_string(image)
            
            return {
                'image': image_path,
                'text': text,
                'engine': 'tesseract'
            }


def main():
    """Main batch processing pipeline"""
    parser = argparse.ArgumentParser(description='Batch process images/videos')
    parser.add_argument('--input', type=str, required=True,
                       help='Input directory')
    parser.add_argument('--mode', type=str, required=True,
                       choices=['detection', 'ocr'],
                       help='Processing mode')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of workers')
    parser.add_argument('--output', type=str, default='results',
                       help='Output directory')
    parser.add_argument('--method', type=str, default='threaded',
                       choices=['sequential', 'threaded', 'multiprocess', 'batched'],
                       help='Processing method')
    
    args = parser.parse_args()
    
    try:
        # Select processor
        if args.mode == 'detection':
            processor = DetectionBatchProcessor(
                batch_size=args.batch_size,
                num_workers=args.workers,
                output_dir=args.output
            )
            process_func = processor.detect_person
        else:  # ocr
            processor = OCRBatchProcessor(
                batch_size=args.batch_size,
                num_workers=args.workers,
                output_dir=args.output
            )
            process_func = processor.extract_text
        
        # Get files
        files = processor.get_files(args.input)
        
        if len(files) == 0:
            logger.error("No files found to process")
            return
        
        # Process files
        start_time = time.time()
        
        if args.method == 'sequential':
            results = processor.process_sequential(files, process_func)
        elif args.method == 'threaded':
            results = processor.process_threaded(files, process_func)
        elif args.method == 'multiprocess':
            results = processor.process_multiprocess(files, process_func)
        else:  # batched
            results = processor.process_batched(files, process_func)
        
        elapsed_time = time.time() - start_time
        
        # Save results
        processor.save_results(results)
        processor.print_summary(elapsed_time)
        
        if len(files) > 0:
            logger.info(f"Average time per file: {elapsed_time/len(files):.2f} seconds")
        
        logger.info(f"✅ Batch processing completed!")
    
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
