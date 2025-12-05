"""
Integration tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_signup_success(client: TestClient):
    """Test successful user signup."""
    response = client.post("/api/v1/auth/signup", json={
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword123",
        "ssn": "123-45-6789",
        "date_of_birth": "1990-01-01",
        "mailing_address": "123 Main St, City, State 12345"
    })

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_signup_duplicate_email(client: TestClient):
    """Test signup with duplicate email fails."""
    # First signup
    client.post("/api/v1/auth/signup", json={
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword123",
        "ssn": "123-45-6789",
        "date_of_birth": "1990-01-01",
        "mailing_address": "123 Main St"
    })

    # Duplicate signup
    response = client.post("/api/v1/auth/signup", json={
        "name": "Jane Doe",
        "email": "john@example.com",
        "password": "anotherpassword",
        "ssn": "987-65-4321",
        "date_of_birth": "1995-01-01",
        "mailing_address": "456 Oak Ave"
    })

    assert response.status_code == 422


def test_login_success(client: TestClient):
    """Test successful login."""
    # Signup first
    client.post("/api/v1/auth/signup", json={
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword123",
        "ssn": "123-45-6789",
        "date_of_birth": "1990-01-01",
        "mailing_address": "123 Main St"
    })

    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "john@example.com",
        "password": "securepassword123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials fails."""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
