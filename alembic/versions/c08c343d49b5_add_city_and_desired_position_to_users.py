"""add city and desired_position to users

Revision ID: c08c343d49b5
Revises: 1be14fe2767b
Create Date: 2026-09-05 13:44:04.460190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c08c343d49b5'
down_revision: Union[str, Sequence[str], None] = '1be14fe2767b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("city", sa.String(), nullable=True))
    op.add_column("users", sa.Column("desired_position", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "desired_position")
    op.drop_column("users", "city")