"""add auth fields and refresh sessions

Revision ID: 003
Revises: 002
Create Date: 2024-10-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    userrole_enum = postgresql.ENUM('USER', 'AUTHOR', 'ADMIN', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)
    
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))
    op.add_column('users', sa.Column('role', sa.Enum('USER', 'AUTHOR', 'ADMIN', name='userrole'), nullable=False, server_default='USER'))
    op.add_column('users', sa.Column('github_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_github_id'), 'users', ['github_id'], unique=True)
    
    op.create_table('refresh_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('refresh_token', sa.Text(), nullable=False),
    sa.Column('user_agent', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_sessions_id'), 'refresh_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_sessions_refresh_token'), 'refresh_sessions', ['refresh_token'], unique=True)
    
    op.execute("UPDATE users SET role = 'AUTHOR' WHERE is_verified_author = true")


def downgrade() -> None:
    op.drop_index(op.f('ix_refresh_sessions_refresh_token'), table_name='refresh_sessions')
    op.drop_index(op.f('ix_refresh_sessions_id'), table_name='refresh_sessions')
    op.drop_table('refresh_sessions')
    
    op.drop_index(op.f('ix_users_github_id'), table_name='users')
    op.drop_column('users', 'github_id')
    op.drop_column('users', 'role')
    op.drop_column('users', 'password_hash')
    
    op.execute("DROP TYPE userrole")

