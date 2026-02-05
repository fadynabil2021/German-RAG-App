"""add_user_roles_and_project_details

Revision ID: 5c225544298d
Revises: 243ca8b683b0
Create Date: 2026-01-31 19:04:16.155378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c225544298d'
down_revision: Union[str, None] = '243ca8b683b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to users table
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=False, server_default='user'))
    op.add_column('users', sa.Column('proficiency_level', sa.String(length=10), nullable=False, server_default='A1'))
    
    # Add columns to projects table
    op.add_column('projects', sa.Column('project_name', sa.String(length=255), nullable=True))
    op.add_column('projects', sa.Column('project_description', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove columns from projects table
    op.drop_column('projects', 'project_description')
    op.drop_column('projects', 'project_name')
    
    # Remove columns from users table
    op.drop_column('users', 'proficiency_level')
    op.drop_column('users', 'role')
