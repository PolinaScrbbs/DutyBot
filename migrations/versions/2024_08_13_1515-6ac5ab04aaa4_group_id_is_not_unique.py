"""group_id is not unique

Revision ID: 6ac5ab04aaa4
Revises: b7342bf56324
Create Date: 2024-08-13 15:15:48.109374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ac5ab04aaa4'
down_revision: Union[str, None] = 'b7342bf56324'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('users_group_id_key', 'users', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('users_group_id_key', 'users', ['group_id'])
    # ### end Alembic commands ###
