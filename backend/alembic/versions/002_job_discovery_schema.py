"""Sprint 2.1 - Expand jobs table with job discovery columns.

Revision ID: 002_job_discovery_schema
Revises: 001_initial_schema
Create Date: 2026-07-03 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_job_discovery_schema'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old jobs table (cascade to remove the FK constraint on applications)
    op.execute("DROP TABLE IF EXISTS jobs CASCADE")

    op.create_table(
        'jobs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portal', sa.String(length=100), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('job_title', sa.String(length=255), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=False),
        sa.Column('apply_url', sa.String(length=750), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('remote', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('salary', sa.String(length=100), nullable=True),
        sa.Column('experience', sa.String(length=100), nullable=True),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.Column('posted_date', sa.DateTime(), nullable=True),
        sa.Column('scraped_date', sa.DateTime(), nullable=False),
        sa.Column('employment_type', sa.String(length=100), nullable=True),
        sa.Column('work_mode', sa.String(length=100), nullable=True),
        sa.Column('source_hash', sa.String(length=64), nullable=False),
        sa.Column('match_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='unprocessed'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_hash', name='uq_jobs_source_hash'),
    )
    op.create_index('ix_jobs_portal', 'jobs', ['portal'])
    op.create_index('ix_jobs_company_name', 'jobs', ['company_name'])
    op.create_index('ix_jobs_job_title', 'jobs', ['job_title'])
    op.create_index('ix_jobs_location', 'jobs', ['location'])
    op.create_index('ix_jobs_remote', 'jobs', ['remote'])
    op.create_index('ix_jobs_work_mode', 'jobs', ['work_mode'])
    op.create_index('ix_jobs_source_hash', 'jobs', ['source_hash'], unique=True)
    op.create_index('ix_jobs_match_score', 'jobs', ['match_score'])
    op.create_index('ix_jobs_status', 'jobs', ['status'])

    # Restore the FK from applications to new jobs table
    op.create_foreign_key(
        'applications_job_id_fkey',
        'applications', 'jobs',
        ['job_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS jobs CASCADE")

    op.create_table(
        'jobs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portal_id', sa.String(length=100), nullable=True),
        sa.Column('portal_name', sa.String(length=100), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('job_title', sa.String(length=255), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=False),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('match_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_foreign_key(
        'applications_job_id_fkey',
        'applications', 'jobs',
        ['job_id'], ['id'],
        ondelete='CASCADE'
    )
