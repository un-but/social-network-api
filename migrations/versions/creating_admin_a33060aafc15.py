"""Creating an admin.

ID миграции: a33060aafc15
Изменяет: 8af847b54434
Дата создания: 19:35:44 22.09.2025 по МСК
"""

import uuid
from collections.abc import Sequence

import bcrypt
import sqlalchemy as sa
from alembic import op

# Идентификаторы миграции, используются Alembic.
revision: str = "a33060aafc15"
down_revision: str | None = "8af847b54434"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    users = sa.table(
        "users",
        sa.column("id", sa.UUID),
        sa.column("is_active", sa.Boolean),
        sa.column("role", sa.String),
        sa.column("name", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
    )

    admin_id = uuid.uuid4()
    password_hash = bcrypt.hashpw(b"admin_password", bcrypt.gensalt()).decode("utf-8")

    op.bulk_insert(
        users,
        [
            {
                "id": admin_id,
                "is_active": True,
                "role": "admin",
                "name": "Admin",
                "email": "admin@example.com",
                "password": password_hash,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM users WHERE email = 'admin@example.com'")
