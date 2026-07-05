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


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Border AI Control System API" in response.json()["message"]


def test_register_user(setup_db):
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_register_duplicate_user(setup_db):
    """Test duplicate user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    client.post("/api/auth/register", json=user_data)
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400


def test_login_user(setup_db):
    """Test user login"""
    # Register user first
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(setup_db):
    """Test login with wrong password"""
    # Register user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Wrong password
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
