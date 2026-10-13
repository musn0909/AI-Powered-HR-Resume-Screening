
"""initial recruitment schema

Revision ID: 4e54b8020932
Revises:
Create Date: 2026-10-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Alembic revision identifiers
revision: str = "4e54b8020932"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recruitment database tables."""

    # Candidates table
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("experience", sa.Integer(), nullable=False),
        sa.UniqueConstraint("email")
    )

    op.create_index(
        "ix_candidates_id",
        "candidates",
        ["id"]
    )

    # Jobs table
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("company", sa.String(150), nullable=False),
        sa.Column("location", sa.String(100), nullable=False),
        sa.Column(
            "required_experience",
            sa.Integer(),
            nullable=False
        )
    )

    op.create_index(
        "ix_jobs_id",
        "jobs",
        ["id"]
    )

    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column(
            "hashed_password",
            sa.String(255),
            nullable=False
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Integer(), nullable=False),
        sa.UniqueConstraint("email")
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"]
    )

    # Applications association table
    op.create_table(
        "applications",
        sa.Column(
            "candidate_id",
            sa.Integer(),
            sa.ForeignKey(
                "candidates.id",
                ondelete="CASCADE"
            ),
            primary_key=True
        ),
        sa.Column(
            "job_id",
            sa.Integer(),
            sa.ForeignKey(
                "jobs.id",
                ondelete="CASCADE"
            ),
            primary_key=True
        )
    )


def downgrade() -> None:
    """Remove recruitment database tables."""

    op.drop_table("applications")

    op.drop_index(
        "ix_users_id",
        table_name="users"
    )
    op.drop_table("users")

    op.drop_index(
        "ix_jobs_id",
        table_name="jobs"
    )
    op.drop_table("jobs")

    op.drop_index(
        "ix_candidates_id",
        table_name="candidates"
    )
    op.drop_table("candidates")
