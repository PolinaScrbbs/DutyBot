"""Group.creator_id is Unique

Revision ID: 518cf788b57d
Revises: 0c79bec7dcf0
Create Date: 2024-09-19 14:38:19.415031
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '518cf788b57d'
down_revision: Union[str, None] = '0c79bec7dcf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_groups_creator_id', ['creator_id'])


def downgrade() -> None:
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_constraint('uq_groups_creator_id', type_='unique')
