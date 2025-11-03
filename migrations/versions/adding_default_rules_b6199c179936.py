"""Adding default rules.

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
        sa.column("full_view", sa.Boolean),
    )

    rules = [
        # Определение доступа к своим объектам у ролей
        *[
            {
                "role": role,
                "object_type": object_type,
                "action": action,
                "owned": True,
                "allowed": True,
                "full_view": role in ("admin", "manager"),
            }
            for role in ("user", "manager", "admin")
            for action in ("create", "read", "update", "delete")
            for object_type in ("users", "posts", "comments", "role_rules")
        ],
        # Определение доступа к чужим объектам у роли user
        *[
            {
                "role": "user",
                "object_type": object_type,
                "action": action,
                "owned": False,
                "allowed": action == "read",
                "full_view": False,
            }
            for action in ("create", "read", "update", "delete")
            for object_type in ("users", "posts", "comments", "role_rules")
        ],
        # Определение доступа к чужим объектам у роли manager
        *[
            {
                "role": "manager",
                "object_type": object_type,
                "action": action,
                "owned": False,
                "allowed": action == "read" or (action == "delete" and object_type != "role_rules"),
                "full_view": True,
            }
            for action in ("create", "read", "update", "delete")
            for object_type in ("users", "posts", "comments", "role_rules")
        ],
        # Определение доступа к чужим объектам у роли admin
        *[
            {
                "role": "admin",
                "object_type": object_type,
                "action": action,
                "owned": False,
                "allowed": True,
                "full_view": True,
            }
            for action in ("create", "read", "update", "delete")
            for object_type in ("users", "posts", "comments", "role_rules")
        ],
    ]

    op.bulk_insert(role_rules, rules)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM role_rules")
