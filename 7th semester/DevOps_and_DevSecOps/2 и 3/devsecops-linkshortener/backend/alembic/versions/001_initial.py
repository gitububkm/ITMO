"""Create initial tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-10-02 17:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

user_role = postgresql.ENUM("USER", "ADMIN", name="user_role", create_type=False)


def upgrade() -> None:
    op.execute("CREATE TYPE user_role AS ENUM ('USER', 'ADMIN')")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("short_code", sa.String(length=32), nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("click_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.UniqueConstraint("short_code", name="uq_links_short_code"),
    )
    op.create_index("ix_links_short_code", "links", ["short_code"], unique=False)

    op.create_table(
        "clicks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "link_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("links.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("clicked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("referer", sa.String(length=512), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_clicks_link_id", "clicks", ["link_id"], unique=False)
    op.create_index("ix_clicks_clicked_at", "clicks", ["clicked_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_clicks_clicked_at", table_name="clicks")
    op.drop_index("ix_clicks_link_id", table_name="clicks")
    op.drop_table("clicks")
    op.drop_index("ix_links_short_code", table_name="links")
    op.drop_table("links")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE user_role")
