"""Add event detail columns (address, contact_email, max_participants).

Revision ID: add_event_details_columns
Revises: add_role_id_to_users
Create Date: 2026-08-16
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_event_details_columns'
down_revision = 'add_role_id_to_users'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('contact_email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('max_participants', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_column('max_participants')
        batch_op.drop_column('contact_email')
        batch_op.drop_column('address')
