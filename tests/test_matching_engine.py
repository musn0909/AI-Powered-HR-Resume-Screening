
from app.matching_engine import match_candidate


def test_matching_skills_and_experience():
    result = match_candidate(
        required_skills=[
            "Python",
            "FastAPI",
            "PostgreSQL"
        ],
        required_experience=3,
        structured_data={
            "skills": [
                "Python", "FastAPI", "Docker"
            ],
            "experience_years": 4,
            "education": ["BS Computer Science"]
        }
    )

    assert result["matched_skills"] == [
        "Python", "FastAPI"
    ]

    assert result["skills_not_found"] == [
        "PostgreSQL"
    ]

    assert (
        result["experience_status"]
        == "stated_requirement_met"
    )

    assert result["review_required"] is True


def test_missing_experience():
    result = match_candidate(
        required_skills=["Python"],
        required_experience=2,
        structured_data={
            "skills": ["Python"],
            "experience_years": None,
            "education": []
        }
    )

    assert (
        result["experience_status"]
        == "not_verified"
    )


def test_case_insensitive_matching():
    result = match_candidate(
        required_skills=["PYTHON"],
        required_experience=1,
        structured_data={
            "skills": ["python"],
            "experience_years": 2
        }
    )

    assert result["matched_skills"] == ["PYTHON"]


def test_missing_skill_does_not_reject():
    result = match_candidate(
        required_skills=["Kubernetes"],
        required_experience=2,
        structured_data={
            "skills": ["Docker"],
            "experience_years": 3
        }
    )

    assert result["skills_not_found"] == [
        "Kubernetes"
    ]

    assert result["review_required"] is True
