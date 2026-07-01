"""Add role_id to users table

Revision ID: add_role_id_to_users
Revises: 39570a1e480c
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_role_id_to_users'
down_revision = '39570a1e480c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
