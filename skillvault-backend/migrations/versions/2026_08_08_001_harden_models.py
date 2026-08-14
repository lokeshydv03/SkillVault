"""Harden models with provenance, lifecycle, strategy, and audit trace columns

Revision ID: 2026_08_08_001
Revises: 
Create Date: 2026-08-08 11:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import pgvector

# revision identifiers, used by Alembic.
revision: str = '2026_08_08_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension if not exists
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Add provenance and lifecycle columns to skills if not exists
    with op.batch_alter_table('skills', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source_type', sa.String(length=32), server_default='BUILTIN', nullable=False))
        batch_op.add_column(sa.Column('created_by', sa.Column('created_by', sa.String(length=32), server_default='SYSTEM', nullable=False)))
        batch_op.add_column(sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index(batch_op.f('ix_skills_source_type'), ['source_type'], unique=False)

    # Add audit trace column to tasks
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('retrieval_trace', sa.JSON(), nullable=True))

    # Add strategy and retrieval_score columns to executions
    with op.batch_alter_table('executions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('strategy', sa.String(length=32), server_default='REUSE', nullable=False))
        batch_op.add_column(sa.Column('retrieval_score', sa.Float(), nullable=True))
        batch_op.create_index(batch_op.f('ix_executions_strategy'), ['strategy'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('executions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_executions_strategy'))
        batch_op.drop_column('retrieval_score')
        batch_op.drop_column('strategy')

    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_column('retrieval_trace')

    with op.batch_alter_table('skills', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_skills_source_type'))
        batch_op.drop_column('last_used_at')
        batch_op.drop_column('created_by')
        batch_op.drop_column('source_type')
