
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()


def test_openapi_schema():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "/auth/login" in schema["paths"]
    assert "/auth/register" in schema["paths"]
    assert "/jobs/{job_id}/matches" in schema["paths"]


def test_protected_user_endpoint():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_resume_upload_requires_login():
    response = client.post(
        "/resumes/upload/1",
        files={
            "file": (
                "sample.pdf",
                b"%PDF-1.4\n",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 401


def test_matching_requires_login():
    response = client.get("/jobs/1/matches")

    assert response.status_code == 401


def test_resume_analysis_requires_login():
    response = client.get("/resumes/1/analysis")

    assert response.status_code == 401
