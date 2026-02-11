"""nullable_election_columns

Revision ID: a14be11ce7ab
Revises: 7b72b070fd66
Create Date: 2026-02-11 14:18:22.696177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a14be11ce7ab'
down_revision: Union[str, Sequence[str], None] = '7b72b070fd66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make election_result columns nullable."""
    op.alter_column('election_result', 'nombre_inscrits',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('election_result', 'nombre_votants',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('election_result', 'nombre_exprimes',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('election_result', 'taux_participation',
               existing_type=sa.NUMERIC(precision=5, scale=2),
               nullable=True)


def downgrade() -> None:
    """Revert election_result columns to NOT NULL."""
    op.alter_column('election_result', 'taux_participation',
               existing_type=sa.NUMERIC(precision=5, scale=2),
               nullable=False)
    op.alter_column('election_result', 'nombre_exprimes',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('election_result', 'nombre_votants',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('election_result', 'nombre_inscrits',
               existing_type=sa.INTEGER(),
               nullable=False)
