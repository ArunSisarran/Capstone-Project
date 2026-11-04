"""add kind to saved_recipes (favorite / saved)

Revision ID: e1b7c4a90d52
Revises: 71be6535529c
Create Date: 2026-11-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1b7c4a90d52'
down_revision: Union[str, None] = '71be6535529c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. New column. Every existing row becomes a 'saved' mark.
    with op.batch_alter_table("saved_recipes") as batch:
        batch.add_column(sa.Column("kind", sa.String(length=16), nullable=False, server_default="saved"))

    # 2. Before the unique constraint can exist, remove accidental duplicates
    #    (the old save endpoint could race). Keep the oldest row of each group.
    op.execute(
        "DELETE FROM saved_recipes WHERE id NOT IN "
        "(SELECT MIN(id) FROM saved_recipes GROUP BY user_id, recipe_id, kind)"
    )

    # 3. The rules: one mark per (user, recipe, kind), and only two kinds.
    with op.batch_alter_table("saved_recipes") as batch:
        batch.create_unique_constraint("uq_saved_user_recipe_kind", ["user_id", "recipe_id", "kind"])
        batch.create_check_constraint("ck_saved_kind", "kind IN ('favorite', 'saved')")


def downgrade() -> None:
    # Note: 'favorite' rows are not removed, so after a downgrade they look like saved recipes.
    with op.batch_alter_table("saved_recipes") as batch:
        batch.drop_constraint("ck_saved_kind", type_="check")
        batch.drop_constraint("uq_saved_user_recipe_kind", type_="unique")
        batch.drop_column("kind")