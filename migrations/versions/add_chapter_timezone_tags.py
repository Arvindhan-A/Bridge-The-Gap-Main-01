"""Add timezone and tags columns to chapters.

Revision ID: add_chapter_timezone_tags
Revises: add_site_stats_table
Create Date: 2026-08-24
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_chapter_timezone_tags'
down_revision = 'add_site_stats_table'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('chapters') as batch_op:
        batch_op.add_column(sa.Column('timezone', sa.String(length=20), server_default='', nullable=True))
        batch_op.add_column(sa.Column('tags', sa.String(length=300), server_default='', nullable=True))


def downgrade():
    with op.batch_alter_table('chapters') as batch_op:
        batch_op.drop_column('tags')
        batch_op.drop_column('timezone')
