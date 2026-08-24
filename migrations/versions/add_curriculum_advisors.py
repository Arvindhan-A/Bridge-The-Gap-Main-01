"""Add curricula, advisors and advisor_initiatives tables.

Revision ID: add_curriculum_advisors
Revises: add_chapter_timezone_tags
Create Date: 2026-08-24
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_curriculum_advisors'
down_revision = 'add_chapter_timezone_tags'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('curricula',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), default=''),
        sa.Column('status', sa.String(length=20), default='in_progress'),
        sa.Column('category', sa.String(length=120), default=''),
        sa.Column('grade_level', sa.String(length=60), default=''),
        sa.Column('file_url', sa.String(length=500), default=''),
        sa.Column('published', sa.Boolean(), default=True),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('advisors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('title', sa.String(length=200), default=''),
        sa.Column('avatar', sa.String(length=500), default=''),
        sa.Column('bio', sa.Text(), default=''),
        sa.Column('published', sa.Boolean(), default=True),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )
    op.create_table('subscribers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('source', sa.String(length=60), default=''),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_table('advisor_initiatives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('advisor_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=120), default=''),
        sa.Column('description', sa.Text(), default=''),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.ForeignKeyConstraint(['advisor_id'], ['advisors.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('advisor_initiatives')
    op.drop_table('subscribers')
    op.drop_table('advisors')
    op.drop_table('curricula')
