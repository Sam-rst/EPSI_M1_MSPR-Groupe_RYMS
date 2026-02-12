"""Remove obsolete v2 tables (territoire, election_result)

Revision ID: 5c74986a8b20
Revises: a14be11ce7ab
Create Date: 2026-02-11 23:58:34.246392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c74986a8b20'
down_revision: Union[str, Sequence[str], None] = 'a14be11ce7ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Remove ALL obsolete v2.0 tables before v3.0 recreation."""
    # 1. Drop FK constraints pointing to territoire table (IF EXISTS)
    op.execute('ALTER TABLE IF EXISTS indicateur DROP CONSTRAINT IF EXISTS indicateur_id_territoire_fkey')
    op.execute('ALTER TABLE IF EXISTS prediction DROP CONSTRAINT IF EXISTS prediction_id_territoire_fkey')

    # 2. Drop ALL v2.0 tables (order: children first, then parents)
    # indicateur depends on type_indicateur via FK
    op.execute('DROP TABLE IF EXISTS indicateur CASCADE')
    op.execute('DROP TABLE IF EXISTS prediction CASCADE')
    op.execute('DROP TABLE IF EXISTS type_indicateur CASCADE')
    op.execute('DROP TABLE IF EXISTS election_result CASCADE')
    op.execute('DROP TABLE IF EXISTS territoire CASCADE')


def downgrade() -> None:
    """Downgrade schema - Not implemented (v2.0 tables obsolete)."""
    # Downgrade vers v2.0 non implémenté car schéma obsolète
    # Pour restaurer, utiliser un backup de la base
    pass
