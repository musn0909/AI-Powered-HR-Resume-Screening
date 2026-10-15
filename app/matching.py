
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.auth import require_roles
from app.database import get_db
from app.matching_engine import match_candidate
from app.models import applications


router = APIRouter(
    prefix="/jobs",
    tags=["Candidate Matching"],
    dependencies=[
        Depends(require_roles("admin", "hr"))
    ]
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/{job_id}/matches")
def get_job_matches(job_id: int, db: DbSession):
    job = db.get(models.Job, job_id)

    if job is None:
        raise HTTPException(404, "Job not found")

    candidates = db.scalars(
        select(models.Candidate)
        .join(
            applications,
            models.Candidate.id ==
            applications.c.candidate_id
        )
        .where(applications.c.job_id == job_id)
        .order_by(models.Candidate.id)
    ).all()

    results = []

    for candidate in candidates:
        # Use latest available analyzed resume
        resume = db.scalars(
            select(models.Resume)
            .where(
                models.Resume.candidate_id == candidate.id,
                models.Resume.structured_data.is_not(None)
            )
            .order_by(models.Resume.uploaded_at.desc(),
                      models.Resume.id.desc())
            .limit(1)
        ).first()

        if resume is None:
            results.append({
                "candidate_id": candidate.id,
                "name": candidate.name,
                "status": "analysis_required",
                "review_required": True
            })
            continue

        comparison = match_candidate(
            required_skills=job.required_skills or [],
            required_experience=job.required_experience,
            structured_data=resume.structured_data
        )

        results.append({
            "candidate_id": candidate.id,
            "name": candidate.name,
            "resume_id": resume.id,
            "status": "ready_for_hr_review",
            "comparison": comparison
        })

    return {
        "job_id": job.id,
        "job_title": job.title,
        "total_applicants": len(candidates),
        "results": results
    }
