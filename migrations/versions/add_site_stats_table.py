"""Add site_stats table.

Revision ID: add_site_stats_table
Revises: add_sponsors_table
Create Date: 2026-08-23
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_site_stats_table'
down_revision = 'add_sponsors_table'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('site_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kits_delivered', sa.Integer(), nullable=True),
        sa.Column('student_chapters', sa.Integer(), nullable=True),
        sa.Column('students_reached', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('site_stats')
