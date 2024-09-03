"""Update Models

Revision ID: b457317e628d
Revises: e011a0203fbb
Create Date: 2024-08-07 09:25:14.610880

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b457317e628d"
down_revision: Union[str, None] = "e011a0203fbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("groups", sa.Column("course_number", sa.Integer(), nullable=False))
    op.drop_constraint("groups_creator_id_key", "groups", type_="unique")
    op.drop_column("groups", "cource_number")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "groups",
        sa.Column("cource_number", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.create_unique_constraint("groups_creator_id_key", "groups", ["creator_id"])
    op.drop_column("groups", "course_number")
    # ### end Alembic commands ###
