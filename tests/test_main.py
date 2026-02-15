"""Tests for main application"""
import pytest


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    # Should serve login page (HTML)
    assert "Community Building Manager" in response.text or "login" in response.text.lower()
