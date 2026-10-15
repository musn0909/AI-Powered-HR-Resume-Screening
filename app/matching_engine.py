
import re


def normalize_skill(skill: str) -> str:
    """Normalize skill names for comparison."""
    return re.sub(r"\s+", " ", skill.strip()).casefold()


def match_candidate(
    required_skills: list[str],
    required_experience: int,
    structured_data: dict
) -> dict:
    """
    Compare job requirements with unverified
    information extracted from a resume.
    """

    candidate_skills = structured_data.get("skills") or []

    # Map normalized skills to original display names
    candidate_lookup = {
        normalize_skill(skill): skill
        for skill in candidate_skills
        if isinstance(skill, str)
    }

    matched_skills = []
    not_found_skills = []

    for skill in required_skills:
        normalized = normalize_skill(skill)

        if normalized in candidate_lookup:
            matched_skills.append(skill)
        else:
            not_found_skills.append(skill)

    experience = structured_data.get("experience_years")

    if isinstance(experience, bool):
        experience = None

    if not isinstance(experience, (int, float)):
        experience = None

    if experience is None:
        experience_status = "not_verified"
    elif experience >= required_experience:
        experience_status = "stated_requirement_met"
    else:
        experience_status = "stated_below_requirement"

    return {
        "matched_skills": matched_skills,
        "skills_not_found": not_found_skills,
        "required_experience": required_experience,
        "stated_experience": experience,
        "experience_status": experience_status,
        "education_found": structured_data.get(
            "education", []
        ),
        "review_required": True,
        "message": (
            "Automated extraction is unverified. "
            "Skills not found are not proof of their absence."
        )
    }
