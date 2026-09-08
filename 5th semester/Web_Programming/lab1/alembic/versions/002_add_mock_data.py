"""add mock data

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    users_table = sa.table('users',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('email', sa.String),
        sa.column('registration_date', sa.DateTime),
        sa.column('is_verified_author', sa.Boolean),
        sa.column('avatar', sa.String)
    )

    op.bulk_insert(users_table, [
        {
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'registration_date': datetime.utcnow(),
            'is_verified_author': True,
            'avatar': 'https://example.com/avatar1.jpg'
        },
        {
            'name': 'Мария Петрова',
            'email': 'maria@example.com',
            'registration_date': datetime.utcnow(),
            'is_verified_author': True,
            'avatar': 'https://example.com/avatar2.jpg'
        },
        {
            'name': 'Алексей Сидоров',
            'email': 'alexey@example.com',
            'registration_date': datetime.utcnow(),
            'is_verified_author': False,
            'avatar': 'https://example.com/avatar3.jpg'
        }
    ])

    news_table = sa.table('news',
        sa.column('id', sa.Integer),
        sa.column('title', sa.String),
        sa.column('content', sa.JSON),
        sa.column('publication_date', sa.DateTime),
        sa.column('author_id', sa.Integer),
        sa.column('cover', sa.String)
    )

    op.bulk_insert(news_table, [
        {
            'title': 'Первая новость',
            'content': {'type': 'article', 'body': 'Содержание первой новости', 'tags': ['новость', 'важное']},
            'publication_date': datetime.utcnow(),
            'author_id': 1,
            'cover': 'https://example.com/cover1.jpg'
        },
        {
            'title': 'Вторая новость',
            'content': {'type': 'article', 'body': 'Содержание второй новости', 'tags': ['обновление']},
            'publication_date': datetime.utcnow(),
            'author_id': 2,
            'cover': 'https://example.com/cover2.jpg'
        }
    ])

    comments_table = sa.table('comments',
        sa.column('id', sa.Integer),
        sa.column('text', sa.String),
        sa.column('news_id', sa.Integer),
        sa.column('author_id', sa.Integer),
        sa.column('publication_date', sa.DateTime)
    )

    op.bulk_insert(comments_table, [
        {
            'text': 'Отличная новость!',
            'news_id': 1,
            'author_id': 2,
            'publication_date': datetime.utcnow()
        },
        {
            'text': 'Интересно, спасибо за информацию',
            'news_id': 1,
            'author_id': 3,
            'publication_date': datetime.utcnow()
        },
        {
            'text': 'Ждем новых обновлений',
            'news_id': 2,
            'author_id': 1,
            'publication_date': datetime.utcnow()
        }
    ])


def downgrade() -> None:
    op.execute("DELETE FROM comments WHERE id IN (1, 2, 3)")
    op.execute("DELETE FROM news WHERE id IN (1, 2)")
    op.execute("DELETE FROM users WHERE id IN (1, 2, 3)")

