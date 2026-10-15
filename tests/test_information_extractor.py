
from app.information_extractor import (
    extract_candidate_information
)


def test_python_backend_resume():
    resume_text = """
    Ali Khan
    Python Backend Developer

    Skills: Python, FastAPI, PostgreSQL, Docker
    Experience: 3 years
    Education: BS Computer Science
    """

    result = extract_candidate_information(
        resume_text
    )

    assert "Python" in result["skills"]
    assert "FastAPI" in result["skills"]
    assert "Docker" in result["skills"]

    assert result["experience_years"] == 3
    assert "BS Computer Science" in result["education"]


def test_resume_without_experience():
    resume_text = """
    Junior Software Developer
    Skills: Python and Git
    Education: BS Computer Science
    """

    result = extract_candidate_information(
        resume_text
    )

    assert result["experience_years"] is None
    assert "Python" in result["skills"]


def test_empty_resume():
    result = extract_candidate_information("")

    assert result["skills"] == []
    assert result["experience_years"] is None
    assert result["education"] == []


def test_skill_matching_does_not_match_fragments():
    result = extract_candidate_information(
        "I enjoy digital photography."
    )

    assert "Git" not in result["skills"]
