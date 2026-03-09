import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.infrastructure.database.base import get_db
from app.core.services.auth_service import hash_password, create_access_token
from app.models.db_models import User
from app.core.entities.models import UserRole

# ─── Mock DB ───

class MockDB:
    def __init__(self):
        self.users = {}
        self.incidents = {}

    def query(self, model):
        return self

    def filter(self, *args):
        return self

    def first(self):
        return None

    def all(self):
        return []

    def add(self, obj):
        pass

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def close(self):
        pass

    def count(self):
        return 0

    def offset(self, n):
        return self

    def limit(self, n):
        return self

    def order_by(self, *args):
        return self


def override_get_db():
    yield MockDB()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ─── Tests ───

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "SafeNZ" in data["app"]


def test_register_duplicate_email():
    """Test that registering with an existing email returns 400."""
    with patch("app.api.routes.auth.UserRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get_by_email.return_value = MagicMock(email="test@test.com")
        response = client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "test@test.com",
            "password": "Password123",
            "role": "citizen",
        })
        assert response.status_code == 400


def test_register_success():
    """Test successful registration."""
    with patch("app.api.routes.auth.UserRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get_by_email.return_value = None
        mock_user = MagicMock()
        mock_user.id = "test-uuid"
        mock_user.name = "Test User"
        mock_user.email = "new@test.com"
        mock_user.phone = None
        mock_user.role = UserRole.CITIZEN
        mock_user.verified = False
        from datetime import datetime
        mock_user.created_at = datetime.utcnow()
        instance.create.return_value = mock_user
        response = client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "new@test.com",
            "password": "Password123",
            "role": "citizen",
        })
        assert response.status_code == 201


def test_login_invalid_credentials():
    """Test login with wrong password returns 401."""
    with patch("app.api.routes.auth.UserRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get_by_email.return_value = None
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "WrongPass",
        })
        assert response.status_code == 401


def test_password_reset_request_always_200():
    """Test that password reset request always returns 200 (prevents email enumeration)."""
    with patch("app.api.routes.auth.UserRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get_by_email.return_value = None
        response = client.post("/api/v1/auth/reset-password/request", json={
            "email": "nonexistent@test.com",
        })
        assert response.status_code == 200


def test_get_incidents_unauthenticated():
    """Test getting incidents list is public."""
    with patch("app.api.routes.incidents.IncidentRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.list_all.return_value = ([], 0)
        response = client.get("/api/v1/incidents")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


def test_create_incident_requires_auth():
    """Test that creating an incident requires authentication."""
    response = client.post("/api/v1/incidents", json={
        "title": "Test Flood",
        "description": "Test",
        "disaster_type": "flood",
        "severity": "medium",
        "latitude": -41.0,
        "longitude": 174.0,
    })
    assert response.status_code == 403


def test_list_alerts_public():
    """Test that alerts list is publicly accessible."""
    with patch("app.api.routes.alerts.AlertRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.list_all.return_value = ([], 0)
        response = client.get("/api/v1/alerts")
        assert response.status_code == 200


def test_list_shelters_public():
    """Test that shelters list is publicly accessible."""
    with patch("app.api.routes.shelters.ShelterRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.list_all.return_value = []
        response = client.get("/api/v1/shelters")
        assert response.status_code == 200


def test_jwt_token_generation():
    """Test JWT token creation and decoding."""
    from app.core.services.auth_service import create_access_token, decode_token
    token = create_access_token({"sub": "user-123"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_password_hashing():
    """Test password hashing and verification."""
    from app.core.services.auth_service import hash_password, verify_password
    hashed = hash_password("MySecurePass123")
    assert verify_password("MySecurePass123", hashed)
    assert not verify_password("WrongPass", hashed)


def test_nearby_incidents_validates_lat():
    """Test that nearby incidents validates latitude range."""
    response = client.get("/api/v1/incidents/nearby?lat=999&lon=174.0")
    assert response.status_code == 422


def test_nearby_shelters_validates_coordinates():
    """Test that nearby shelters validates coordinates."""
    response = client.get("/api/v1/shelters/nearby?lat=200&lon=174.0")
    assert response.status_code == 422
