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


def test_queue_status(setup_db):
    """Test queue status endpoint"""
    response = client.get("/api/queue/status")
    assert response.status_code == 200
    data = response.json()
    assert "waiting" in data
    assert "in_progress" in data
    assert "completed" in data


def test_add_to_queue(setup_db):
    """Test adding person to queue"""
    # Create a person first
    person_data = {
        "detection_id": "DET_001",
        "age_estimated": 30
    }
    person_response = client.post("/api/detection/person", json=person_data)
    person_id = person_response.json()["id"]
    
    # Add to queue
    queue_data = {
        "person_id": person_id,
        "priority": "normal"
    }
    response = client.post("/api/queue/person", json=queue_data)
    assert response.status_code == 200
    assert response.json()["status"] == "waiting"


def test_list_queue(setup_db):
    """Test listing queue entries"""
    response = client.get("/api/queue")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
