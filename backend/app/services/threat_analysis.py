import logging
from typing import Dict, List, Optional, Tuple
import pickle
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ThreatAnalysisService:
    """Service for threat analysis and risk assessment"""
    
    def __init__(self, model_path: str = None, threat_db_path: str = None):
        """
        Initialize threat analysis service
        
        Args:
            model_path: Path to threat analysis model
            threat_db_path: Path to threat database
        """
        self.model_path = model_path or "/app/models/threat_analysis.pkl"
        self.threat_db_path = threat_db_path or "/app/models/threat_database.json"
        self.model = None
        self.threat_database = []
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize threat analysis models"""
        try:
            # Load threat analysis model if exists
            if Path(self.model_path).exists():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Threat analysis model loaded: {self.model_path}")
            else:
                logger.warning(f"Threat model not found: {self.model_path}")
            
            # Load threat database
            self._load_threat_database()
        
        except Exception as e:
            logger.error(f"Error initializing threat analysis: {str(e)}")
    
    def _load_threat_database(self):
        """Load threat database"""
        try:
            if Path(self.threat_db_path).exists():
                import json
                with open(self.threat_db_path, 'r') as f:
                    self.threat_database = json.load(f)
                logger.info(f"Threat database loaded: {len(self.threat_database)} threats")
            else:
                # Use sample threat database
                self.threat_database = self._get_sample_threats()
                logger.info("Using sample threat database")
        
        except Exception as e:
            logger.error(f"Error loading threat database: {str(e)}")
            self.threat_database = self._get_sample_threats()
    
    def analyze_person(self, person_data: Dict) -> Dict:
        """
        Analyze person for threat indicators
        
        Args:
            person_data: Person data dictionary
            
        Returns:
            Dictionary with threat analysis results
        """
        try:
            threat_score = 0.0
            threat_indicators = []
            
            # Check document status
            if person_data.get("document_status") == "suspicious":
                threat_score += 0.3
                threat_indicators.append("Suspicious document")
            
            # Check behavioral flags
            if person_data.get("behavioral_flags"):
                threat_score += 0.2
                threat_indicators.append("Behavioral anomaly detected")
            
            # Check against threat database
            matches = self._check_threat_database(person_data)
            if matches:
                threat_score += 0.4
                for match in matches:
                    threat_indicators.append(f"Threat match: {match['type']}")
            
            # Normalize score to 0-1 range
            threat_score = min(1.0, threat_score)
            
            logger.info(f"Threat analysis complete for person: {person_data.get('id')}, score: {threat_score}")
            
            return {
                "success": True,
                "person_id": person_data.get("id"),
                "threat_score": threat_score,
                "threat_level": self._calculate_threat_level(threat_score),
                "indicators": threat_indicators,
                "matches": matches,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error analyzing person: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "threat_score": 0.0,
                "indicators": []
            }
    
    def _check_threat_database(self, person_data: Dict) -> List[Dict]:
        """
        Check person against threat database
        
        Args:
            person_data: Person data
            
        Returns:
            List of matching threats
        """
        matches = []
        
        # Check against known threats (simple matching)
        for threat in self.threat_database:
            if person_data.get("name") and threat.get("name"):
                if person_data["name"].lower() == threat["name"].lower():
                    matches.append(threat)
            
            # Check document match
            if person_data.get("document_number") == threat.get("document_number"):
                matches.append(threat)
        
        return matches[:5]  # Return top 5 matches
    
    def analyze_document(self, document_data: Dict) -> Dict:
        """
        Analyze document for authenticity and fraud indicators
        
        Args:
            document_data: Document data
            
        Returns:
            Dictionary with document analysis results
        """
        try:
            authenticity_score = 1.0
            fraud_indicators = []
            
            # Check document format
            if not self._validate_document_format(document_data):
                authenticity_score -= 0.3
                fraud_indicators.append("Invalid document format")
            
            # Check OCR quality
            if document_data.get("ocr_confidence", 1.0) < 0.7:
                authenticity_score -= 0.2
                fraud_indicators.append("Low OCR confidence")
            
            # Check field consistency
            if not self._validate_field_consistency(document_data):
                authenticity_score -= 0.2
                fraud_indicators.append("Inconsistent fields")
            
            # Check expiry
            if self._is_document_expired(document_data):
                authenticity_score -= 0.1
                fraud_indicators.append("Document expired")
            
            authenticity_score = max(0.0, min(1.0, authenticity_score))
            
            logger.info(f"Document analysis complete: {document_data.get('id')}, authenticity: {authenticity_score}")
            
            return {
                "success": True,
                "document_id": document_data.get("id"),
                "authenticity_score": authenticity_score,
                "is_authentic": authenticity_score > 0.7,
                "fraud_indicators": fraud_indicators,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "authenticity_score": 0.0,
                "fraud_indicators": []
            }
    
    @staticmethod
    def _calculate_threat_level(score: float) -> str:
        """Calculate threat level from score"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    @staticmethod
    def _validate_document_format(document_data: Dict) -> bool:
        """Validate document format"""
        required_fields = ["document_type", "holder_name", "document_number"]
        return all(document_data.get(field) for field in required_fields)
    
    @staticmethod
    def _validate_field_consistency(document_data: Dict) -> bool:
        """Validate field consistency"""
        # Check if dates are consistent
        issue_date = document_data.get("issue_date")
        expiry_date = document_data.get("expiry_date")
        
        if issue_date and expiry_date:
            try:
                from datetime import datetime
                issue = datetime.strptime(issue_date, "%Y-%m-%d")
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                return issue < expiry
            except:
                return False
        
        return True
    
    @staticmethod
    def _is_document_expired(document_data: Dict) -> bool:
        """Check if document is expired"""
        from datetime import datetime
        expiry_date = document_data.get("expiry_date")
        if expiry_date:
            try:
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                return expiry < datetime.now()
            except:
                return False
        return False
    
    @staticmethod
    def _get_sample_threats() -> List[Dict]:
        """Get sample threat database"""
        return [
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
