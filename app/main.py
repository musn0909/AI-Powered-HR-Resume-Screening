
from contextlib import asynccontextmanager
from typing import Annotated
from app.models import applications
from app.resumes import router as resumes_router
from fastapi import Security
from app.auth import router as auth_router, require_roles
from app.matching import router as matching_router
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app.database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Candidate Management API",
    lifespan=lifespan
)
app.include_router(auth_router)
app.include_router(resumes_router)
app.include_router(matching_router)


DbSession = Annotated[Session, Depends(get_db)]


@app.get("/")
def home():
    return {"message": "FastAPI PostgreSQL Connected"}


# CREATE - Add a candidate
@app.post(
    "/candidates",
    response_model=schemas.CandidateResponse,
    status_code=201
)
def create_candidate(
    candidate: schemas.CandidateCreate,
    db: DbSession
):
    new_candidate = models.Candidate(
        **candidate.model_dump()
    )

    db.add(new_candidate)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Candidate email already exists"
        )

    db.refresh(new_candidate)
    return new_candidate


# READ - Get all candidates
@app.get(
    "/candidates",
    response_model=list[schemas.CandidateResponse]
)
def get_candidates(db: DbSession):
    result = db.scalars(
        select(models.Candidate).order_by(models.Candidate.id)
    )
    return result.all()


# READ - Get one candidate
@app.get(
    "/candidates/{candidate_id}",
    response_model=schemas.CandidateResponse
)
def get_candidate(candidate_id: int, db: DbSession):
    candidate = db.get(models.Candidate, candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate


# UPDATE - Update a candidate
@app.put(
    "/candidates/{candidate_id}",
    response_model=schemas.CandidateResponse
)
def update_candidate(
    candidate_id: int,
    updated: schemas.CandidateCreate,
    db: DbSession
):
    candidate = db.get(models.Candidate, candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    for field, value in updated.model_dump().items():
        setattr(candidate, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Candidate email already exists"
        )

    db.refresh(candidate)
    return candidate


# DELETE - Delete a candidate
@app.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: DbSession):
    candidate = db.get(models.Candidate, candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    db.delete(candidate)
    db.commit()

    return {"message": "Candidate deleted successfully"}


# CREATE JOB
@app.post(
    "/jobs",
    response_model=schemas.JobResponse,
    status_code=201
)
def create_job(job: schemas.JobCreate, db: DbSession):
    new_job = models.Job(**job.model_dump())

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# GET ALL JOBS
@app.get(
    "/jobs",
    response_model=list[schemas.JobResponse]
)
def get_jobs(db: DbSession):
    return db.scalars(
        select(models.Job).order_by(models.Job.id)
    ).all()


# GET ONE JOB
@app.get(
    "/jobs/{job_id}",
    response_model=schemas.JobResponse
)
def get_job(job_id: int, db: DbSession):
    job = db.get(models.Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


# APPLY FOR A JOB
@app.post(
    "/jobs/{job_id}/apply/{candidate_id}",
    status_code=201
)
def apply_for_job(
    job_id: int,
    candidate_id: int,
    db: DbSession
):
    job = db.get(models.Job, job_id)
    candidate = db.get(models.Candidate, candidate_id)

    if job is None:
        raise HTTPException(404, "Job not found")

    if candidate is None:
        raise HTTPException(404, "Candidate not found")

    existing = db.execute(
        select(applications.c.candidate_id).where(
            applications.c.candidate_id == candidate_id,
            applications.c.job_id == job_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Candidate already applied"
        )

    db.execute(
        applications.insert().values(
            candidate_id=candidate_id,
            job_id=job_id
        )
    )
    db.commit()

    return {
        "message": "Application submitted",
        "candidate_id": candidate_id,
        "job_id": job_id
    }


# GET CANDIDATES FOR A JOB
@app.get(
    "/jobs/{job_id}/candidates",
    response_model=list[schemas.CandidateResponse]
)
def get_job_candidates(job_id: int, db: DbSession):
    job = db.get(models.Job, job_id)

    if job is None:
        raise HTTPException(404, "Job not found")

    statement = (
        select(models.Candidate)
        .join(
            applications,
            models.Candidate.id ==
            applications.c.candidate_id
        )
        .where(applications.c.job_id == job_id)
        .order_by(models.Candidate.id)
    )

    return db.scalars(statement).all()


# GET JOBS APPLIED TO BY A CANDIDATE
@app.get(
    "/candidates/{candidate_id}/jobs",
    response_model=list[schemas.JobResponse]
)
def get_candidate_jobs(
    candidate_id: int,
    db: DbSession
):
    candidate = db.get(models.Candidate, candidate_id)

    if candidate is None:
        raise HTTPException(404, "Candidate not found")

    statement = (
        select(models.Job)
        .join(
            applications,
            models.Job.id == applications.c.job_id
        )
        .where(
            applications.c.candidate_id == candidate_id
        )
        .order_by(models.Job.id)
    )

    return db.scalars(statement).all()
