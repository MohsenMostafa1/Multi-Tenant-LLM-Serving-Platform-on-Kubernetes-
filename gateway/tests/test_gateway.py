import pytest
from fastapi.testclient import TestClient
import sys
sys.path.append(".")
from app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_completions_no_token():
    response = client.post("/v1/completions", json={"prompt": "Hi"})
    assert response.status_code == 401
