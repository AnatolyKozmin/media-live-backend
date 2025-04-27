"""Fix telegram ID and username tg

Revision ID: c6369170039c
Revises: 937813c4d061
Create Date: 2025-04-27 17:53:57.318514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6369170039c'
down_revision: Union[str, None] = '937813c4d061'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
