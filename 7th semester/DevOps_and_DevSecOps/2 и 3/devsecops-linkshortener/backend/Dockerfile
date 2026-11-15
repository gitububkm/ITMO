FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir "poetry>=2.4.3,<2.5.0"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --without dev --no-interaction --no-ansi && \
    groupadd --system app && \
    useradd --system --gid app --home-dir /app --no-create-home --shell /usr/sbin/nologin app && \
    mkdir -p /app/logs && \
    chown app:app /app /app/logs

# Copy only what the runtime needs (no recursive `COPY . .`, which could leak local files into the image)
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app app ./app

USER app

CMD ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
