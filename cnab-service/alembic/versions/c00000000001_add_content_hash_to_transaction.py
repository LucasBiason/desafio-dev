"""Add content_hash column to cnab_transaction for deduplication.

Revision ID: c00000000001
Revises: b00000000001
Create Date: 2026-04-06
"""

import sqlalchemy as sa

from alembic import op

revision = "c00000000001"
down_revision = "b00000000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cnab_transaction", sa.Column("content_hash", sa.String(64), nullable=True))
    op.create_unique_constraint("uq_transaction_content_hash", "cnab_transaction", ["content_hash"])


def downgrade() -> None:
    op.drop_constraint("uq_transaction_content_hash", "cnab_transaction", type_="unique")
    op.drop_column("cnab_transaction", "content_hash")
