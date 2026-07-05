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


def test_detection_status(setup_db):
    """Test detection status endpoint"""
    response = client.get("/api/detection/status")
    assert response.status_code == 200
    data = response.json()
    assert "total_detected" in data
    assert "in_queue" in data
    assert "flagged" in data
    assert "cleared" in data


def test_create_person_detection(setup_db):
    """Test creating person detection"""
    person_data = {
        "detection_id": "DET_001",
        "age_estimated": 30,
        "gender": "male",
        "height": 180.0,
        "detection_confidence": 0.95
    }
    response = client.post("/api/detection/person", json=person_data)
    assert response.status_code == 200
    assert response.json()["detection_id"] == "DET_001"


def test_list_persons(setup_db):
    """Test listing persons"""
    # Create a person
    person_data = {
        "detection_id": "DET_001",
        "age_estimated": 30,
        "gender": "male"
    }
    client.post("/api/detection/person", json=person_data)
    
    # List persons
    response = client.get("/api/detection/persons")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_person(setup_db):
    """Test getting person details"""
    # Create a person
    person_data = {
        "detection_id": "DET_001",
        "age_estimated": 30
    }
    create_response = client.post("/api/detection/person", json=person_data)
    person_id = create_response.json()["id"]
    
    # Get person
    response = client.get(f"/api/detection/person/{person_id}")
    assert response.status_code == 200
    assert response.json()["id"] == person_id


def test_update_person(setup_db):
    """Test updating person"""
    # Create a person
    person_data = {
        "detection_id": "DET_001",
        "age_estimated": 30
    }
    create_response = client.post("/api/detection/person", json=person_data)
    person_id = create_response.json()["id"]
    
    # Update person
    update_data = {"status": "flagged"}
    response = client.put(f"/api/detection/person/{person_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "flagged"
