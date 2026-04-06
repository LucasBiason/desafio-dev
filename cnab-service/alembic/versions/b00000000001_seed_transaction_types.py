"""seed transaction types

Revision ID: b00000000001
Revises: 96d9e7a430b0
Create Date: 2026-04-02
"""
from typing import Sequence, Union

import uuid
from alembic import op
from sqlalchemy import Boolean, table, column, String, SmallInteger
from sqlalchemy.dialects.postgresql import UUID

revision: str = "b00000000001"
down_revision: Union[str, None] = "96d9e7a430b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TRANSACTION_TYPES = [
    (1, "Débito", "entrada", "+"),
    (2, "Boleto", "saída", "-"),
    (3, "Financiamento", "saída", "-"),
    (4, "Crédito", "entrada", "+"),
    (5, "Recebimento Empréstimo", "entrada", "+"),
    (6, "Vendas", "entrada", "+"),
    (7, "Recebimento TED", "entrada", "+"),
    (8, "Recebimento DOC", "entrada", "+"),
    (9, "Aluguel", "saída", "-"),
]


def upgrade() -> None:
    tt = table(
        "cnab_transaction_type",
        column("id", UUID(as_uuid=True)),
        column("code", SmallInteger),
        column("description", String),
        column("nature", String),
        column("sign", String),
        column("is_active", Boolean),
    )
    op.bulk_insert(tt, [
        {"id": str(uuid.uuid4()), "code": code, "description": desc, "nature": nature, "sign": sign, "is_active": True}
        for code, desc, nature, sign in TRANSACTION_TYPES
    ])


def downgrade() -> None:
    op.execute("DELETE FROM cnab_transaction_type WHERE code IN (1,2,3,4,5,6,7,8,9)")
