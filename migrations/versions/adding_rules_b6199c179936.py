"""Adding rules.

ID миграции: b6199c179936
Изменяет: a33060aafc15
Дата создания: 14:47:09 04.10.2025 по МСК
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Идентификаторы миграции, используются Alembic.
revision: str = "b6199c179936"
down_revision: str | None = "a33060aafc15"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Таблица правил для ролей
    role_rules = sa.table(
        "role_rules",
        sa.column("role", sa.String),
        sa.column("object_type", sa.String),
        sa.column("action", sa.String),
        sa.column("owned", sa.Boolean),
        sa.column("allowed", sa.Boolean),
    )

    rules = [
        # Разрешение доступа к своим объектам всем по умолчанию
        *[
            {
                "role": role,
                "object_type": object_type,
                "action": action,
                "owned": True,
                "allowed": True,
            }
            for role in ("user", "manager", "admin")
            for action in ("create", "read", "update", "delete")
            for object_type in ("users", "posts", "comments", "role_rules")
        ],
        # Права для роли user
        *[
            {
                "role": "user",
                "object_type": object_type,
                "action": action,
                "owned": False,
                "allowed": action == "read",
            }
            for action in ("create", "read", "update", "delete")
            for object_type in ("users", "posts", "comments", "role_rules")
        ],
        # Правила для роли manager
        *[
            {
                "role": "manager",
                "object_type": object_type,
                "action": action,
                "owned": False,
                "allowed": action in ("read", "delete"),
            }
            for action in ("create", "read", "update", "delete")
            for object_type in ("users", "posts", "comments")
        ],
        # Правила для роли admin
        *[
            {
                "role": "admin",
                "object_type": object_type,
                "action": action,
                "owned": False,
                "allowed": True,
            }
            for action in ("create", "read", "update", "delete")
            for object_type in ("users", "posts", "comments", "role_rules")
        ],
    ]

    op.bulk_insert(role_rules, rules)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM role_rules")
