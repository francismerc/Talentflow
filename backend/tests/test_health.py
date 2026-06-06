from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "TalentFlow AI API is healthy.",
        "data": {
            "status": "healthy",
            "version": "0.1.0",
        },
    }
