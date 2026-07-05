# ML Models & Scripts - Comprehensive Summary

## Overview
This document provides a detailed breakdown of all ML models, initialization processes, and service implementations in the Border AI Control System.

---

## 1. Model Initialization System

### 1.1 ModelLoader (`backend/app/ml/model_loader.py`)
**Purpose:** Central manager for loading and caching ML models

**Key Components:**
```
Class: ModelLoader
├── __init__(model_dir: str = "/app/models")
├── load_detection_model() → YOLOv8 model
├── load_ocr_model() → EasyOCR model
└── get_model(model_name: str) → cached model
```

**Detection Model Loading:**
- Loads pre-trained YOLOv8 Medium model (`yolov8m.pt`)
- Path: `/app/models/yolov8m.pt`
- Framework: Ultralytics YOLO v8
- Handles missing model gracefully with warnings

**OCR Model Loading:**
- Loads EasyOCR Reader for English (`en`)
- Language: English only (configurable in code)
- Lazy-loads model on first use
- Alternative: Tesseract via pytesseract

**Error Handling:**
- Logs warnings if model files missing
- Returns `None` on load failure
- Cached in `self.models` dictionary for reuse

---

## 2. Detection Service Implementation

### 2.1 PersonDetectionService (`backend/app/services/person_detection.py`)
**Purpose:** Real-time person detection and tracking using YOLOv8

**Class Methods:**

#### `detect_persons(image_path: str, confidence: float = 0.5) → Dict`
**Functionality:**
- Runs YOLOv8 inference on single image
- Filters results for person class only (COCO class 0)
- Returns bounding boxes with confidence scores

**Output Structure:**
```json
{
  "success": true,
  "image_path": "path/to/image.jpg",
  "persons_detected": 3,
  "detections": [
    {
      "confidence": 0.95,
      "bbox": [x1, y1, x2, y2],
      "area": 15000.5
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Key Features:**
- Bounding box format: `[x1, y1, x2, y2]` (pixel coordinates)
- Area calculation: `(x2-x1) * (y2-y1)`
- Configurable confidence threshold (default: 0.5)
- File existence validation

#### `detect_from_video(video_path: str, frame_skip: int = 1) → Dict`
**Functionality:**
- Processes video frame-by-frame
- Frame skipping to reduce computation (1 = every frame, 2 = every 2nd frame, etc.)
- Returns detections per frame with frame indices

**Output Structure:**
```json
{
  "success": true,
  "video_path": "path/to/video.mp4",
  "total_frames": 300,
  "frames_with_detections": 45,
  "detections_by_frame": [
    {
      "frame": 0,
      "detections": [
        {
          "confidence": 0.92,
          "bbox": [x1, y1, x2, y2]
        }
      ]
    }
  ]
}
```

**Performance Notes:**
- Returns max 100 frames (first 100 with detections)
- Uses OpenCV (`cv2.VideoCapture`)
- Releases video capture on completion/error

**Configuration (via `config.py`):**
```python
MODEL_PERSON_DETECTION = "yolov8m.pt"
MODEL_PERSON_DETECTION_CONFIDENCE = 0.5
MAX_DETECTION_PERSONS = 50
DETECTION_FPS = 30
```

---

## 3. OCR Service

### 3.1 DocumentOCRService (`backend/app/services/document_ocr.py`)
**Purpose:** Extract text and structured fields from document images

**Supported Engines:**
1. **Tesseract** (default) - via pytesseract
2. **EasyOCR** - neural network-based, higher accuracy

**Class Methods:**

#### `extract_text(image_path: str) → Dict`
**Tesseract Output:**
```json
{
  "success": true,
  "image_path": "path/to/doc.jpg",
  "text": "John Doe\nPassport: AB123456\nIssue: 2020-01-01",
  "confidence": 0.85,
  "engine": "tesseract"
}
```

**EasyOCR Output:**
```json
{
  "success": true,
  "image_path": "path/to/doc.jpg",
  "text": "John Doe Passport: AB123456",
  "confidence": 0.88,
  "engine": "easyocr",
  "details": [
    [[bbox_coords], "John", 0.92],
    [[bbox_coords], "Doe", 0.91]
  ]
}
```

**Key Differences:**
- Tesseract: Faster, lower accuracy, traditional OCR
- EasyOCR: Slower, higher accuracy, returns bounding boxes

#### `extract_fields(image_path: str) → Dict`
**Structured Field Extraction:**
```json
{
  "success": true,
  "image_path": "path/to/doc.jpg",
  "fields": {
    "name": "John Doe",
    "date_of_birth": "01/01/1990",
    "document_number": "AB123456",
    "expiry_date": "01/01/2030",
    "nationality": "USA"
  },
  "raw_text": "full extracted text",
  "confidence": 0.85
}
```

**Field Extraction Logic:**

| Field | Extraction Method |
|-------|-------------------|
| **Name** | Uppercase words with 2+ parts |
| **DOB** | Regex pattern `\d{1,2}[/-]\d{1,2}[/-]\d{2,4}` |
| **Document#** | Pattern `[A-Z]{0,2}\d{6,9}` |
| **Expiry** | Date after "expiry" or "valid until" keyword |
| **Nationality** | Hardcoded country list (USA, UK, CANADA, etc.) |

**Limitations:**
- Name extraction: Simple uppercase detection (can miss edge cases)
- Hardcoded countries: Limited to predefined list
- Date parsing: Basic regex (no validation logic)
- **Note:** Extraction methods are placeholder implementations meant for enhancement

---

## 4. Threat Analysis Model

### 4.1 ThreatAnalysisService (`backend/app/services/threat_analysis.py`)
**Purpose:** Multi-factor threat assessment and intelligence matching

**Model Initialization:**
- Loads pickled ML model: `/app/models/threat_analysis.pkl` (if exists)
- Loads threat database JSON: `/app/models/threat_database.json` (or fallback to sample)
- Falls back to sample threats if files missing

#### `analyze_person(person_data: Dict) → Dict`
**Threat Scoring Algorithm:**
```
Total Score = (components weighted)
├─ Document Status: +0.3 if suspicious
├─ Behavioral Flags: +0.2 if anomalies detected
├─ Threat DB Match: +0.4 if matches found
└─ Final Score: clamped to [0.0, 1.0]
```

**Threat Level Mapping:**
| Score | Level |
|-------|-------|
| ≥ 0.8 | CRITICAL |
| 0.6-0.79 | HIGH |
| 0.4-0.59 | MEDIUM |
| < 0.4 | LOW |

**Output:**
```json
{
  "success": true,
  "person_id": "PERSON123",
  "threat_score": 0.65,
  "threat_level": "HIGH",
  "indicators": [
    "Suspicious document",
    "Behavioral anomaly detected",
    "Threat match: smuggling_suspect"
  ],
  "matches": [
    {
      "id": "T002",
      "name": "Jane Smuggler",
      "type": "smuggling_suspect",
      "severity": "high",
      "document_number": "CD789012"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Sample Threat Database:**
```python
[
  {
    "id": "T001",
    "name": "John Terrorist",
    "type": "known_threat",
    "severity": "critical",
    "document_number": "AB123456",
    "last_seen": "2024-01-01"
  },
  {
    "id": "T002",
    "name": "Jane Smuggler",
    "type": "smuggling_suspect",
    "severity": "high",
    "document_number": "CD789012",
    "last_seen": "2024-01-05"
  }
]
```

**Threat Matching Logic:**
- Name matching: Case-insensitive string comparison
- Document matching: Exact number comparison
- Returns top 5 matches (limited to prevent overload)

#### `analyze_document(document_data: Dict) → Dict`
**Authenticity Scoring:**
```
Authenticity Score = 1.0
├─ Invalid format: -0.3
├─ Low OCR confidence (<0.7): -0.2
├─ Field inconsistency: -0.2
└─ Expired: -0.1
```

**Output:**
```json
{
  "success": true,
  "document_id": "DOC123",
  "authenticity_score": 0.75,
  "is_authentic": true,
  "fraud_indicators": [],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Document Validation Checks:**
1. **Format Validation:** Required fields present
   - `document_type`, `holder_name`, `document_number`
2. **Field Consistency:** Issue date < Expiry date
3. **OCR Quality:** Confidence score threshold (0.7)
4. **Expiry Check:** Compare `expiry_date` to current date

---

## 5. Risk Calculator Service

### 5.1 RiskCalculatorService (`backend/app/services/risk_calculator.py`)
**Purpose:** Weighted multi-factor risk scoring

**Risk Weight Distribution:**
```python
{
  "behavioral": 0.25,    # 25%
  "document": 0.25,      # 25%
  "biometric": 0.20,     # 20%
  "intelligence": 0.30   # 30% (highest priority)
}
```

#### `calculate_risk_score(risk_factors: Dict) → Dict`
**Input Structure:**
```python
risk_factors = {
  "behavioral_risk": 0.5,          # 0.0-1.0
  "document_risk": 0.3,            # 0.0-1.0
  "biometric_risk": 0.2,           # 0.0-1.0
  "intelligence_match_risk": 0.8   # 0.0-1.0
}
```

**Calculation:**
```
Final Score = (0.5 × 0.25) + (0.3 × 0.25) + (0.2 × 0.20) + (0.8 × 0.30)
            = 0.125 + 0.075 + 0.04 + 0.24
            = 0.48 (MEDIUM)
```

**Output:**
```json
{
  "success": true,
  "risk_score": 0.48,
  "risk_level": "MEDIUM",
  "components": {
    "behavioral": 0.5,
    "document": 0.3,
    "biometric": 0.2,
    "intelligence": 0.8
  },
  "weights": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### `get_risk_indicators(person_data: Dict) → List[str]`
**Risk Flag Detection:**
- Age outside normal range (< 18 or > 65)
- Expired or suspicious documents
- Low detection confidence (< 0.7)
- Behavioral anomalies

**Example Output:**
```python
[
  "Age outside normal range: 73",
  "Expired document",
  "Low detection confidence: 0.65",
  "Behavioral: suspicious_movement"
]
```

---

## 6. ML Inference Engine

### 6.1 InferenceEngine (`backend/app/ml/inference.py`)
**Purpose:** Unified interface for all ML model inference

**Class Methods:**

#### `detect_persons(image_path: str, confidence: float = 0.5) → Dict`
- Wraps PersonDetectionService
- Returns detection results with bounding boxes
- Handles model loading failures

#### `extract_text(image_path: str) → Dict`
- Wraps DocumentOCRService
- Returns extracted text and metadata
- Supports both Tesseract and EasyOCR

---

## 7. Configuration Management

### 7.1 ML Configuration (`backend/app/config.py`)
```python
# Detection
MODEL_PERSON_DETECTION = "yolov8m.pt"
MODEL_PERSON_DETECTION_CONFIDENCE = 0.5
MAX_DETECTION_PERSONS = 50
DETECTION_FPS = 30

# OCR
MODEL_OCR_ENGINE = "tesseract"  # or "easyocr"

# Threat Analysis
THREAT_MODEL_PATH = "/app/models/threat_analysis.pkl"
THREAT_ANALYSIS_ENABLED = True
THREAT_THRESHOLD = 0.6

# Models Directory
MODEL_CACHE_DIR = "/app/models"
```

---

## 8. Model Files & Data Flow

### 8.1 Expected Directory Structure
```
/app/models/
├── yolov8m.pt              # YOLOv8 Medium (197 MB)
├── threat_analysis.pkl     # Pickled threat model
└── threat_database.json    # Threat intelligence data
```

### 8.2 Data Flow Architecture
```
Input Image/Video
    ↓
[PersonDetectionService]
    ├─→ YOLOv8 Inference
    ├─→ COCO Class Filtering (person = 0)
    └─→ Bounding Box + Confidence
    ↓
[DocumentOCRService]
    ├─→ Tesseract or EasyOCR
    ├─→ Text Extraction
    └─→ Field Parsing
    ↓
[RiskCalculatorService]
    ├─→ Weighted Scoring
    ├─→ Component Analysis
    └─→ Risk Level Classification
    ↓
[ThreatAnalysisService]
    ├─→ Threat DB Matching
    ├─→ Document Authenticity
    └─→ Threat Intelligence
    ↓
Final Risk Assessment
```

---

## 9. Dependencies & Requirements

### 9.1 Key ML Dependencies (`backend/requirements.txt`)
```
ultralytics==8.0.231      # YOLOv8
torch==2.1.1              # PyTorch
torchvision==0.16.1       # Vision utilities
tensorflow==2.14.0        # Alternative DL framework
opencv-python==4.8.1.78   # Computer vision
opencv-contrib-python==4.8.1.78
easyocr==1.7.0            # Neural OCR
pytesseract==0.3.10       # Tesseract wrapper
scikit-learn==1.3.2       # ML utilities
pillow==10.1.0            # Image processing
numpy==1.24.3             # Numerical computing
pyyaml==6.0               # YAML parsing
tqdm==4.66.0              # Progress bars
pandas==2.0.0             # Data processing
```

---

## 10. Model Training & Batch Processing

### 10.1 Training Scripts Available
```bash
backend/scripts/
├── train_threat_model.py           # ✅ Train threat classifier
├── finetune_yolov8.py              # ✅ Fine-tune detection model
├── batch_processor.py              # ✅ Batch processing pipeline
└── evaluate_models.py              # Generate evaluation reports
```

### 10.2 Training Pipeline Features
- **Threat Model Training:**
  - RandomForest & GradientBoosting support
  - Data preprocessing (scaling, encoding, handling missing values)
  - Train/test split with stratification
  - Comprehensive metrics (accuracy, precision, recall, F1, ROC-AUC)
  - Feature importance analysis

- **YOLOv8 Fine-tuning:**
  - Multiple model variants (nano→xlarge)
  - GPU acceleration support
  - Early stopping with patience
  - Model validation & testing
  - Export to ONNX/TorchScript

- **Batch Processing:**
  - 4 processing methods (sequential, threaded, multiprocess, batched)
  - Detection & OCR batch processors
  - Progress tracking
  - Error handling & recovery
  - JSON results export

---

## 11. Performance Considerations

### 11.1 Detection Service
- **Model Size:** YOLOv8 Medium (~197 MB)
- **Inference Time:** ~50-100ms per image (GPU), ~300-500ms (CPU)
- **Memory:** ~2GB during inference
- **Optimization:** Frame skipping in video processing reduces load

### 11.2 OCR Service
- **Tesseract:** Fast (~200-500ms), lower accuracy
- **EasyOCR:** Slower (~500-1500ms), higher accuracy
- **Batch Processing:** Not implemented in single processor (use batch_processor.py)

### 11.3 Risk Calculation
- **Speed:** < 1ms (simple weighted sum)
- **Bottleneck:** Threat DB matching (linear search)
- **Optimization:** Consider indexing threat database for larger datasets

---

## 12. Error Handling & Logging

All services implement:
- Logger configuration at module level
- Try-except blocks with graceful fallbacks
- Structured error responses with `success: false`
- File existence validation before processing
- Model load verification with warnings

---

## 13. Testing & Validation

### 13.1 Test Location
```
backend/tests/
```

### 13.2 Run Tests
```bash
cd backend
pytest
```

### 13.3 Recommended Tests to Add
- [ ] Detection accuracy on sample images
- [ ] OCR confidence scoring validation
- [ ] Risk score edge cases (0.0, 1.0, >1.0)
- [ ] Threat DB matching performance
- [ ] Video processing with various codecs
- [ ] Model loading with missing files

---

## Summary

| Component | Technology | Status |
|-----------|-----------|--------|
| **Detection** | YOLOv8 | ✅ Implemented |
| **OCR** | Tesseract/EasyOCR | ✅ Implemented |
| **Threat Analysis** | Pickle + JSON DB | ✅ Implemented |
| **Risk Scoring** | Weighted Algorithm | ✅ Implemented |
| **Model Training** | scikit-learn/ultralytics | ✅ Implemented |
| **Batch Processing** | ThreadPool/ProcessPool | ✅ Implemented |
| **Model Fine-tuning** | YOLOv8 | ✅ Implemented |
| **GPU Support** | PyTorch/CUDA | ✅ Configurable |

---

**Last Updated:** 2024-01-15  
**Author:** Border AI Development Team
