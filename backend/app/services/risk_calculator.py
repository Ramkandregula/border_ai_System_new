import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskCalculatorService:
    """Service for calculating overall risk scores"""
    
    def __init__(self):
        """Initialize risk calculator"""
        self.risk_weights = {
            "behavioral": 0.25,
            "document": 0.25,
            "biometric": 0.20,
            "intelligence": 0.30
        }
    
    def calculate_risk_score(self, risk_factors: Dict) -> Dict:
        """
        Calculate overall risk score
        
        Args:
            risk_factors: Dictionary with different risk components
            
        Returns:
            Dictionary with risk score and level
        """
        try:
            weighted_score = 0.0
            
            # Behavioral risk
            behavioral = risk_factors.get("behavioral_risk", 0.0)
            weighted_score += behavioral * self.risk_weights["behavioral"]
            
            # Document risk
            document = risk_factors.get("document_risk", 0.0)
            weighted_score += document * self.risk_weights["document"]
            
            # Biometric risk
            biometric = risk_factors.get("biometric_risk", 0.0)
            weighted_score += biometric * self.risk_weights["biometric"]
            
            # Intelligence risk
            intelligence = risk_factors.get("intelligence_match_risk", 0.0)
            weighted_score += intelligence * self.risk_weights["intelligence"]
            
            # Normalize to 0-1 range
            risk_score = min(1.0, max(0.0, weighted_score))
            
            risk_level = self._get_risk_level(risk_score)
            
            logger.info(f"Risk score calculated: {risk_score} ({risk_level})")
            
            return {
                "success": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "components": {
                    "behavioral": behavioral,
                    "document": document,
                    "biometric": biometric,
                    "intelligence": intelligence
                },
                "weights": self.risk_weights,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "risk_score": 0.0,
                "risk_level": "UNKNOWN"
            }
    
    def get_risk_indicators(self, person_data: Dict) -> List[str]:
        """
        Get risk indicators for a person
        
        Args:
            person_data: Person data
            
        Returns:
            List of risk indicators
        """
        indicators = []
        
        # Check age
        age = person_data.get("age_estimated")
        if age and (age < 18 or age > 65):
            indicators.append(f"Age outside normal range: {age}")
        
        # Check document status
        if person_data.get("document_status") == "expired":
            indicators.append("Expired document")
        elif person_data.get("document_status") == "suspicious":
            indicators.append("Suspicious document detected")
        
        # Check detection confidence
        if person_data.get("detection_confidence", 1.0) < 0.7:
            indicators.append(f"Low detection confidence: {person_data.get('detection_confidence')}")
        
        # Check behavioral flags
        if person_data.get("behavioral_flags"):
            for flag in person_data["behavioral_flags"]:
                indicators.append(f"Behavioral: {flag}")
        
        return indicators
    
    @staticmethod
    def _get_risk_level(score: float) -> str:
        """Get risk level from score"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
