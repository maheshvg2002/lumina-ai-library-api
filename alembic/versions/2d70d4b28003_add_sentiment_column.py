"""add_sentiment_column

Revision ID: 2d70d4b28003
Revises: 2cfcd1e375e0
Create Date: 2026-02-21 15:44:12.541976

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d70d4b28003'
down_revision: Union[str, None] = '2cfcd1e375e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the missing sentiment column to the reviews table
    op.add_column('reviews', sa.Column('sentiment', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the sentiment column if rolling back
    op.drop_column('reviews', 'sentiment')