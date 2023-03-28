"""Update URL field length

Revision ID: 7eaafaa65b32
Revises: e83263a5def4
Create Date: 2023-03-28 11:24:39.089063

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7eaafaa65b32"
down_revision = "e83263a5def4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "apiecoindex",
        "url",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=4096),
    )


def downgrade() -> None:
    op.alter_column(
        "apiecoindex",
        "url",
        existing_type=sa.String(length=4096),
        type_=sa.String(length=2048),
    )
