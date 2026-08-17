"""add assignments table

Revision ID: b1f2c3d4a5b6
Revises: ac4589372b44
Create Date: 2026-08-12 14:38:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1f2c3d4a5b6'
down_revision: Union[str, Sequence[str], None] = 'ac4589372b44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assignments_id'), 'assignments', ['id'], unique=False)
    op.create_index(op.f('ix_assignments_agent_id'), 'assignments', ['agent_id'], unique=False)
    op.create_index(op.f('ix_assignments_client_id'), 'assignments', ['client_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assignments_client_id'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_agent_id'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_id'), table_name='assignments')
    op.drop_table('assignments')
