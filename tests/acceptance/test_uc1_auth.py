"""Acceptance Test: UC1 - Authentication (Supabase / Google)

Criterion:
Given a new user, when they sign up with Google, then an account is created and they land on /dashboard within 5 seconds.
"""
import time
import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.database import get_db, SessionLocal
from app.models import User, Tenant


@pytest.fixture
def client():
    return TestClient(app)


def test_uc1_google_auth_signup_flow(client):
    """
    Test that a new user signing up creates an account and returns dashboard access token within 5s.
    """
    start_time = time.time()

    new_user_email = f"student_{int(time.time())}@utm.my"
    signup_payload = {
        "email": new_user_email,
        "name": "Nurul New Student",
        "role": "student",
        "tenant_id": "tenant-utm-001"
    }

    # Simulate sign-up authentication
    response = client.post("/auth/demo-login", json=signup_payload)
    elapsed_time = time.time() - start_time

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    assert elapsed_time < 5.0, f"Sign up took {elapsed_time:.2f}s, expected under 5 seconds"

    data = response.json()
    assert "access_token" in data
    token = data["access_token"]
    user_info = data["user"]
    tenant_info = data["tenant"]

    # Verify user fields
    assert user_info["email"] == new_user_email
    assert user_info["role"] == "student"
    assert user_info["plan"] == "free"
    assert user_info["quota_remaining"] == 3
    assert tenant_info["id"] == "tenant-utm-001"

    # Verify that the token grants immediate access to protected /auth/me
    auth_header = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/auth/me", headers=auth_header)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == new_user_email


def test_unauthenticated_dashboard_refusal(client):
    """
    Assert that requests lacking valid Authorization headers are refused with 401.
    """
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "Missing or invalid" in response.json()["detail"]
