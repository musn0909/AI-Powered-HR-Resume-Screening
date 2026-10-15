
from app.matching_engine import match_candidate


def test_matching():
    result = match_candidate(
        required_skills=[
            "Python",
            "FastAPI",
            "PostgreSQL"
        ],
        required_experience=3,
        structured_data={
            "skills": ["Python", "FastAPI", "Docker"],
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


def test_missing_experience():
    result = match_candidate(
        required_skills=["Python"],
        required_experience=2,
        structured_data={
            "skills": [],
            "experience_years": None,
            "education": []
        }
    )

    assert result["experience_status"] == "not_verified"
    assert result["review_required"] is True
