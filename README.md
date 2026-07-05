# Border AI Control System

An intelligent AI-powered border control system for automated person detection, document verification, threat analysis, and intelligent routing at border checkpoints.

## 🎯 Features

### Core Functionality
- **Person Detection & Tracking**: Real-time computer vision for detecting and tracking individuals
- **Document Recognition**: OCR-based document scanning and verification
- **Threat Analysis**: AI-powered threat assessment system
- **Risk Scoring**: Dynamic risk calculation based on multiple factors
- **Queue Management**: Intelligent queue prioritization
- **Officer Dashboard**: Real-time monitoring and control interface
- **Audit Logs**: Complete activity tracking for compliance

## 📦 Project Structure

```
border_ai_System_new/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   └── ml/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── ml_models/
│   ├── detection/
│   ├── document_ocr/
│   └── threat_analysis/
├── docker-compose.yml
├── .env.example
└── docs/
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/Ramkandregula/border_ai_System_new.git
cd border_ai_System_new

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up -d

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000
```

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh token

### Detection & Tracking
- `POST /api/detection/stream` - Start camera stream
- `GET /api/detection/status` - Get detection status
- `POST /api/detection/person` - Record person detection

### Documents
- `POST /api/documents/scan` - Scan document
- `GET /api/documents/{id}` - Get document details
- `POST /api/documents/{id}/verify` - Verify document

### Risk Assessment
- `POST /api/risk/calculate` - Calculate risk score
- `GET /api/risk/history` - Get risk assessment history
- `GET /api/risk/threats` - Get threat list

### Queue Management
- `GET /api/queue/status` - Get queue status
- `POST /api/queue/person` - Add person to queue
- `PUT /api/queue/{id}` - Update queue position

### Dashboard
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/dashboard/analytics` - Get analytics data
- `GET /api/dashboard/alerts` - Get active alerts

## 🔐 Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Encrypted sensitive data
- Audit logging for all operations
- Rate limiting on API endpoints
- CORS security headers
- SQL injection prevention
- HTTPS/TLS support

## 📊 Database Schema

Key tables:
- `users` - System users
- `persons` - Detected persons
- `documents` - Scanned documents
- `risk_assessments` - Risk analysis records
- `queue_entries` - Queue management
- `audit_logs` - Complete activity logs
- `alerts` - System alerts
- `detection_frames` - Video frames storage

## 🤖 ML Models

### 1. Person Detection (YOLOv8)
- Real-time person detection from video/images
- Multi-person tracking
- Bounding box generation

### 2. Document OCR
- Document type classification
- Text extraction
- Field validation

### 3. Threat Analysis
- Behavioral analysis
- Document authenticity check
- Risk score calculation

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd ../frontend
npm test
```

## 📖 Documentation

- [Backend API Documentation](./docs/API.md)
- [ML Model Details](./docs/ML_MODELS.md)
- [Database Schema](./docs/DATABASE.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Architecture](./docs/ARCHITECTURE.md)

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/border_ai

# API
API_SECRET_KEY=your-secret-key
API_ALGORITHM=HS256
API_TOKEN_EXPIRE_MINUTES=30

# ML Models
MODEL_PERSON_DETECTION=yolov8m.pt
MODEL_OCR_ENGINE=tesseract

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 🚢 Deployment

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for:
- Production deployment
- Kubernetes setup
- Cloud deployment (AWS, Azure, GCP)
- Performance optimization
- Monitoring & Logging

## 📝 License

MIT License - See LICENSE file

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for Border Security**