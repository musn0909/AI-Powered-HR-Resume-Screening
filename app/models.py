
from sqlalchemy import (
    Column, Integer, String, JSON,
    Table, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


# Association table
applications = Table(
    "applications",
    Base.metadata,
    Column(
        "candidate_id",
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "job_id",
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    skills = Column(JSON, nullable=False)
    experience = Column(Integer, nullable=False)

    jobs = relationship(
        "Job",
        secondary=applications,
        back_populates="candidates",
        passive_deletes=True
    )


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    company = Column(String(150), nullable=False)
    location = Column(String(100), nullable=False)
    required_experience = Column(
        Integer, nullable=False
    )

    candidates = relationship(
        "Candidate",
        secondary=applications,
        back_populates="jobs",
        passive_deletes=True
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        default="candidate"
    )

    is_active = Column(
        Integer,
        nullable=False,
        default=1
    )
