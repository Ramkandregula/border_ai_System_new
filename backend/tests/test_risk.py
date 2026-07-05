import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_db():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_calculate_risk(setup_db):
    """Test risk calculation"""
    # First create a person
    person_data = {
        "detection_id": "DET_001",
        "age_estimated": 30
    }
    person_response = client.post("/api/detection/person", json=person_data)
    person_id = person_response.json()["id"]
    
    # Calculate risk
    risk_data = {
        "person_id": person_id,
        "behavioral_risk": 0.3,
        "document_risk": 0.2,
        "biometric_risk": 0.1
    }
    response = client.post("/api/risk/calculate", json=risk_data)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert 0.0 <= data["risk_score"] <= 1.0


def test_get_risk_history(setup_db):
    """Test getting risk history"""
    response = client.get("/api/risk/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_threats(setup_db):
    """Test getting threat list"""
    response = client.get("/api/risk/threats")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
