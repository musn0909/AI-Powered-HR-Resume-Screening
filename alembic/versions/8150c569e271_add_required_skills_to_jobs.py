"""add required skills to jobs

Revision ID: 8150c569e271
Revises: ddc8ddf4e33b
Create Date: 2026-10-15 09:36:13.940485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8150c569e271'
down_revision: Union[str, Sequence[str], None] = 'ddc8ddf4e33b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column(
            "required_skills",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json")
        )
    )



def downgrade() -> None:
    op.drop_column("jobs", "required_skills")
