
"""add phone to candidates

Revision ID: 56ae296dbb34
Revises: 4e54b8020932
Create Date: 2026-10-13 13:28:19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = "56ae296dbb34"

down_revision: Union[str, Sequence[str], None] = (
    "4e54b8020932"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add phone column to candidates table."""

    op.add_column(
        "candidates",
        sa.Column(
            "phone",
            sa.String(length=20),
            nullable=True
        )
    )


def downgrade() -> None:
    """Remove phone column from candidates table."""

    op.drop_column(
        "candidates",
        "phone"
    )
