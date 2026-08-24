"""Add sponsors table.

Revision ID: add_sponsors_table
Revises: add_event_details_columns
Create Date: 2026-08-16
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_sponsors_table'
down_revision = 'add_event_details_columns'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('sponsors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('logo', sa.String(length=500), default=''),
        sa.Column('website', sa.String(length=500), default=''),
        sa.Column('description', sa.Text(), default=''),
        sa.Column('published', sa.Boolean(), default=True),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('sponsors')
