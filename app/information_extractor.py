
import re


SKILL_ALIASES = {
    "Python": ["python"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "SQL": ["sql"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Git": ["git"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs"],
    "Machine Learning": ["machine learning"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "REST API": ["rest api", "restful api"],
}

EDUCATION_PATTERNS = {
    "BS Computer Science":
        r"\b(?:bs|bsc|bachelor(?:'s)?)"
        r"\s+(?:in\s+|of\s+)?computer science\b",

    "BS Software Engineering":
        r"\b(?:bs|bsc|bachelor(?:'s)?)"
        r"\s+(?:in\s+|of\s+)?software engineering\b",

    "MS Computer Science":
        r"\b(?:ms|msc|master(?:'s)?)"
        r"\s+(?:in\s+|of\s+)?computer science\b",

    "MBA":
        r"\bmba\b",
}


def find_phrase(text: str, phrase: str) -> bool:
    pattern = (
        r"(?<!\w)"
        + re.escape(phrase)
        + r"(?!\w)"
    )
    return re.search(
        pattern, text, flags=re.IGNORECASE
    ) is not None


def extract_skills(text: str) -> list[str]:
    found = []

    for skill, aliases in SKILL_ALIASES.items():
        if any(find_phrase(text, a) for a in aliases):
            found.append(skill)

    return found


def extract_experience(text: str) -> int | None:
    patterns = [
        r"\bexperience\s*:\s*(\d{1,2})"
        r"\s*(?:\+?\s*years?|yrs?)\b",

        r"\b(\d{1,2})\s*\+?\s*"
        r"(?:years?|yrs?)\s+of\s+experience\b",

        r"\b(\d{1,2})\s*\+?\s*"
        r"(?:years?|yrs?)\s+of\s+"
        r"(?:professional|work|backend|software)"
        r"\s+(?:development\s+)?experience\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern, text, flags=re.IGNORECASE
        )
        if match:
            return int(match.group(1))

    return None


def extract_education(text: str) -> list[str]:
    education = []

    for degree, pattern in EDUCATION_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            education.append(degree)

    return education


def extract_candidate_information(text: str) -> dict:
    return {
        "skills": extract_skills(text),
        "experience_years": extract_experience(text),
        "education": extract_education(text),
        "extraction_method": "rule_based_v1"
    }
