"""Migration 003: Change DateTime columns to TIMESTAMP WITH TIME ZONE.

Revision ID: 003_timezone_timestamps
Revises: 002_job_discovery_schema
Create Date: 2026-07-03 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_timezone_timestamps'
down_revision: Union[str, None] = '002_job_discovery_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert candidates timestamps
    op.alter_column('candidates', 'created_at',
        existing_type=sa.DateTime(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False)

    # Convert jobs timestamps
    for col in ['posted_date', 'scraped_date', 'created_at']:
        op.alter_column('jobs', col,
            existing_type=sa.DateTime(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=(col == 'posted_date'))

    # Convert applications timestamps
    op.alter_column('applications', 'submitted_at',
        existing_type=sa.DateTime(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False)


def downgrade() -> None:
    for col in ['posted_date', 'scraped_date', 'created_at']:
        op.alter_column('jobs', col,
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=(col == 'posted_date'))

    op.alter_column('candidates', 'created_at',
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False)

    op.alter_column('applications', 'submitted_at',
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False)
