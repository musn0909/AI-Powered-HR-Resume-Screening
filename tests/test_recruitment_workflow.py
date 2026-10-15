
import io
import uuid

from docx import Document
from fastapi.testclient import TestClient

from app.main import app
from app import models, resumes
from app.database import SessionLocal
from app.settings import settings


def create_sample_docx():
    """Generate a sample DOCX resume in memory."""

    document = Document()

    document.add_paragraph("Ali Khan")
    document.add_paragraph("Python Backend Developer")
    document.add_paragraph(
        "Skills: Python, FastAPI, PostgreSQL, Docker"
    )
    document.add_paragraph("Experience: 3 years")
    document.add_paragraph(
        "Education: BS Computer Science"
    )

    file_buffer = io.BytesIO()
    document.save(file_buffer)

    return file_buffer.getvalue()


def test_complete_hr_workflow(tmp_path, monkeypatch):
    """
    Test the complete HR recruitment workflow:

    1. Register user
    2. Assign HR role in isolated test database
    3. Login and get JWT
    4. Create candidate
    5. Create job
    6. Apply candidate to job
    7. Upload resume
    8. Extract text
    9. Analyze resume
    10. Match candidate with job
    """

    # SAFETY: Only run against the test database.
    assert settings.db_name == "candidate_test_db", (
        "Integration tests must use candidate_test_db"
    )

    # Store uploaded test resumes in a temporary folder.
    monkeypatch.setattr(
        resumes,
        "UPLOAD_DIR",
        tmp_path
    )

    # Unique email to avoid duplicate registration errors.
    email = f"hr-{uuid.uuid4().hex}@example.com"
    password = "TestPassword123!Secure"

    with TestClient(app) as client:

        # ----------------------------------
        # STEP 1: Register test user
        # ----------------------------------
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password
            }
        )

        assert response.status_code == 201, response.text

        user_id = response.json()["id"]

        # ----------------------------------
        # STEP 2: Assign HR role
        # ----------------------------------
        # Development fixture only.
        # Public registration must not assign HR roles.

        with SessionLocal() as db:
            user = db.get(models.User, user_id)

            assert user is not None

            user.role = "hr"
            db.commit()

        # ----------------------------------
        # STEP 3: Login using JWT
        # ----------------------------------
        response = client.post(
            "/auth/login",
            data={
                "username": email,
                "password": password
            }
        )

        assert response.status_code == 200, response.text

        token = response.json()["access_token"]

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # ----------------------------------
        # STEP 4: Verify HR authentication
        # ----------------------------------
        response = client.get(
            "/auth/me",
            headers=headers
        )

        assert response.status_code == 200, response.text
        assert response.json()["role"] == "hr"

        # ----------------------------------
        # STEP 5: Create candidate
        # ----------------------------------
        response = client.post(
            "/candidates",
            headers=headers,
            json={
                "name": "Ali Khan",
                "email": (
                    f"candidate-{uuid.uuid4().hex}"
                    "@example.com"
                ),
                "skills": [
                    "Python",
                    "FastAPI"
                ],
                "experience": 3
            }
        )

        assert response.status_code == 201, response.text

        candidate_id = response.json()["id"]

        # ----------------------------------
        # STEP 6: Create job
        # ----------------------------------
        response = client.post(
            "/jobs",
            headers=headers,
            json={
                "title": "Python Backend Developer",
                "company": "Test Company",
                "location": "Lahore",
                "required_experience": 3,
                "required_skills": [
                    "Python",
                    "FastAPI",
                    "PostgreSQL"
                ]
            }
        )

        assert response.status_code == 201, response.text

        job_id = response.json()["id"]

        # ----------------------------------
        # STEP 7: Apply candidate to job
        # ----------------------------------
        response = client.post(
            f"/jobs/{job_id}/apply/{candidate_id}",
            headers=headers
        )

        assert response.status_code == 201, response.text

        # ----------------------------------
        # STEP 8: Upload DOCX resume
        # ----------------------------------
        response = client.post(
            f"/resumes/upload/{candidate_id}",
            headers=headers,
            files={
                "file": (
                    "sample_resume.docx",
                    create_sample_docx(),
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                )
            }
        )

        assert response.status_code == 201, response.text

        resume_id = response.json()["id"]

        # ----------------------------------
        # STEP 9: Extract resume text
        # ----------------------------------
        response = client.post(
            f"/resumes/{resume_id}/extract",
            headers=headers
        )

        assert response.status_code == 200, response.text

        # ----------------------------------
        # STEP 10: Analyze resume
        # ----------------------------------
        response = client.post(
            f"/resumes/{resume_id}/analyze",
            headers=headers
        )

        assert response.status_code == 200, response.text

        structured = response.json()["structured_data"]

        assert "Python" in structured["skills"]
        assert "FastAPI" in structured["skills"]
        assert structured["experience_years"] == 3

        # ----------------------------------
        # STEP 11: Match candidate with job
        # ----------------------------------
        response = client.get(
            f"/jobs/{job_id}/matches",
            headers=headers
        )

        assert response.status_code == 200, response.text

        results = response.json()["results"]

        assert len(results) == 1

        assert (
            results[0]["candidate_id"]
            == candidate_id
        )

        comparison = results[0]["comparison"]

        assert "Python" in comparison["matched_skills"]

        assert comparison["review_required"] is True
