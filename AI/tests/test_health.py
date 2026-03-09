import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure AI root is importable in CI regardless of pytest cwd.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rooftop_fastapi import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
