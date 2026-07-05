import pytest
from app.services.risk_calculator import RiskCalculatorService
from app.services.queue_manager import QueueManagerService
from datetime import datetime


class TestRiskCalculator:
    """Test risk calculator service"""
    
    def test_calculate_risk_score(self):
        """Test risk score calculation"""
        service = RiskCalculatorService()
        
        risk_factors = {
            "behavioral_risk": 0.3,
            "document_risk": 0.2,
            "biometric_risk": 0.1,
            "intelligence_match_risk": 0.4
        }
        
        result = service.calculate_risk_score(risk_factors)
        
        assert result["success"] is True
        assert 0.0 <= result["risk_score"] <= 1.0
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def test_get_risk_indicators(self):
        """Test getting risk indicators"""
        service = RiskCalculatorService()
        
        person_data = {
            "age_estimated": 15,
            "document_status": "expired"
        }
        
        indicators = service.get_risk_indicators(person_data)
        
        assert len(indicators) > 0
        assert any("age" in ind.lower() for ind in indicators)


class TestQueueManager:
    """Test queue manager service"""
    
    def test_get_next_in_queue(self):
        """Test getting next in queue"""
        service = QueueManagerService()
        
        queue_entries = [
            {"id": 1, "priority": "normal", "status": "waiting", "created_at": datetime.utcnow()},
            {"id": 2, "priority": "high", "status": "waiting", "created_at": datetime.utcnow()},
            {"id": 3, "priority": "low", "status": "waiting", "created_at": datetime.utcnow()}
        ]
        
        next_entry = service.get_next_in_queue(queue_entries)
        
        assert next_entry is not None
        assert next_entry["priority"] == "high"
    
    def test_calculate_wait_time(self):
        """Test wait time calculation"""
        service = QueueManagerService()
        
        wait_time = service.calculate_wait_time(position=5, avg_processing_time=10.0)
        
        assert wait_time == 40.0
    
    def test_get_queue_statistics(self):
        """Test queue statistics"""
        service = QueueManagerService()
        
        queue_entries = [
            {"id": 1, "status": "waiting"},
            {"id": 2, "status": "in_progress"},
            {"id": 3, "status": "completed"},
            {"id": 4, "status": "waiting"}
        ]
        
        stats = service.get_queue_statistics(queue_entries)
        
        assert stats["waiting"] == 2
        assert stats["in_progress"] == 1
        assert stats["completed"] == 1
        assert stats["total"] == 4
