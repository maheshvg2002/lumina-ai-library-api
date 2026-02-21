"""add_topic_tag_to_user_preferences

Revision ID: 2cfcd1e375e0
Revises: b0c5df82238b
Create Date: 2026-02-21 12:02:28.372505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cfcd1e375e0'
down_revision: Union[str, None] = 'b0c5df82238b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This creates the column when the reviewer runs docker compose up
    op.add_column('user_preferences', sa.Column('topic_tag', sa.String(), nullable=True))


def downgrade() -> None:
    # This deletes the column if the database needs to be rolled back
    op.drop_column('user_preferences', 'topic_tag')