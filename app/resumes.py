
import os
import uuid
import zipfile
from pathlib import Path
from typing import Annotated
from app.extractor import extract_resume_text
from sqlalchemy.exc import SQLAlchemyError
from app.information_extractor import extract_candidate_information

from fastapi import (
    APIRouter, Depends, File,
    HTTPException, UploadFile
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.auth import require_roles
from app.database import get_db


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
    dependencies=[
        Depends(require_roles("admin", "hr"))
    ]
)

UPLOAD_DIR = Path(
    os.getenv("UPLOAD_DIR", "data/resumes")
)

MAX_SIZE = 5 * 1024 * 1024

MIME_TYPES = {
    ".pdf": "application/pdf",
    ".docx": (
        "application/vnd.openxmlformats-"
        "officedocument.wordprocessingml.document"
    )
}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DbSession = Annotated[Session, Depends(get_db)]


def serialize_resume(resume):
    return {
        "id": resume.id,
        "candidate_id": resume.candidate_id,
        "original_filename": resume.original_filename,
        "file_size": resume.file_size,
        "content_type": resume.content_type,
        "uploaded_at": resume.uploaded_at
    }


def validate_saved_file(path: Path, ext: str):
    if ext == ".pdf":
        with path.open("rb") as f:
            if f.read(5) != b"%PDF-":
                raise HTTPException(
                    400, "Invalid PDF signature"
                )

    elif ext == ".docx":
        if not zipfile.is_zipfile(path):
            raise HTTPException(
                400, "Invalid DOCX format"
            )

        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if "word/document.xml" not in names:
                raise HTTPException(
                    400, "Invalid Word document"
                )


@router.post("/upload/{candidate_id}", status_code=201)
def upload_resume(
    candidate_id: int,
    file: Annotated[UploadFile, File()],
    db: DbSession
):
    candidate = db.get(
        models.Candidate, candidate_id
    )

    if candidate is None:
        raise HTTPException(404, "Candidate not found")

    original = Path(
        (file.filename or "").replace("\\", "/")
    ).name

    ext = Path(original).suffix.lower()

    if ext not in MIME_TYPES:
        raise HTTPException(
            400, "Only PDF and DOCX are accepted"
        )

    stored_name = f"{uuid.uuid4().hex}{ext}"
    saved_path = UPLOAD_DIR / stored_name
    file_size = 0

    try:
        with saved_path.open("xb") as output:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > MAX_SIZE:
                    raise HTTPException(
                        413, "Maximum file size is 5 MB"
                    )

                output.write(chunk)

        if file_size == 0:
            raise HTTPException(400, "Empty file")

        validate_saved_file(saved_path, ext)

        resume = models.Resume(
            candidate_id=candidate_id,
            original_filename=original[:255],
            stored_filename=stored_name,
            content_type=MIME_TYPES[ext],
            file_size=file_size
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return serialize_resume(resume)

    except Exception:
        db.rollback()
        saved_path.unlink(missing_ok=True)
        raise

    finally:
        file.file.close()


@router.get("/candidate/{candidate_id}")
def list_candidate_resumes(
    candidate_id: int,
    db: DbSession
):
    candidate = db.get(
        models.Candidate, candidate_id
    )

    if candidate is None:
        raise HTTPException(404, "Candidate not found")

    resumes = db.scalars(
        select(models.Resume)
        .where(
            models.Resume.candidate_id == candidate_id
        )
        .order_by(models.Resume.id.desc())
    ).all()

    return [serialize_resume(r) for r in resumes]


@router.get("/{resume_id}/download")
def download_resume(
    resume_id: int,
    db: DbSession
):
    resume = db.get(models.Resume, resume_id)

    if resume is None:
        raise HTTPException(404, "Resume not found")

    path = UPLOAD_DIR / resume.stored_filename

    if not path.is_file():
        raise HTTPException(
            404, "Stored resume file not found"
        )

    return FileResponse(
        path=path,
        media_type=resume.content_type,
        filename=resume.original_filename,
        content_disposition_type="attachment"
    )

# EXTRACT TEXT FROM UPLOADED RESUME
@router.post("/{resume_id}/extract")
def extract_resume(
    resume_id: int,
    db: DbSession
):
    resume = db.get(models.Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    storage_root = UPLOAD_DIR.resolve()
    file_path = (
        storage_root / resume.stored_filename
    ).resolve()

    # Prevent paths outside private storage
    if file_path.parent != storage_root:
        raise HTTPException(
            status_code=400,
            detail="Invalid stored file path"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Resume file is missing"
        )

    try:
        extracted_text = extract_resume_text(
            file_path
        )

    except (ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="Resume could not be parsed"
        ) from exc

    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No readable text found. "
                "The resume may require OCR."
            )
        )

    resume.extracted_text = extracted_text

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save extracted text"
        )

    return {
        "message": "Resume text extracted successfully",
        "resume_id": resume.id,
        "characters_extracted": len(extracted_text)
    }


# GET EXTRACTED RESUME TEXT
@router.get("/{resume_id}/text")
def get_resume_text(
    resume_id: int,
    db: DbSession
):
    resume = db.get(models.Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    if resume.extracted_text is None:
        raise HTTPException(
            status_code=404,
            detail="Resume text has not been extracted"
        )

    return {
        "resume_id": resume.id,
        "candidate_id": resume.candidate_id,
        "filename": resume.original_filename,
        "extracted_text": resume.extracted_text
    }

# EXTRACT STRUCTURED CANDIDATE INFORMATION
@router.post("/{resume_id}/analyze")
def analyze_resume(
    resume_id: int,
    db: DbSession
):
    resume = db.get(models.Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    if not resume.extracted_text:
        raise HTTPException(
            status_code=422,
            detail=(
                "Resume text has not been extracted. "
                "Run the /extract endpoint first."
            )
        )

    structured = extract_candidate_information(
        resume.extracted_text
    )

    resume.structured_data = structured

    try:
        db.commit()
        db.refresh(resume)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save structured data"
        )

    return {
        "message": "Resume analyzed successfully",
        "resume_id": resume.id,
        "candidate_id": resume.candidate_id,
        "structured_data": resume.structured_data
    }


# GET STRUCTURED RESUME INFORMATION
@router.get("/{resume_id}/analysis")
def get_resume_analysis(
    resume_id: int,
    db: DbSession
):
    resume = db.get(models.Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    if resume.structured_data is None:
        raise HTTPException(
            status_code=404,
            detail="Resume has not been analyzed"
        )

    return {
        "resume_id": resume.id,
        "candidate_id": resume.candidate_id,
        "structured_data": resume.structured_data
    }
