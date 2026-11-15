FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# gcc and libpq headers are needed to build psycopg2 (pulled in by django-heroku)
RUN apt-get update \
    && apt-get install --no-install-recommends -y gcc libc6-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# gunicorn is not listed in upstream requirements.txt, only used by the Procfile
RUN pip install -r requirements.txt gunicorn==23.0.0

COPY . .

# The SQLite database is created inside the image. No collectstatic: upstream CSS
# references missing fonts, and with DEBUG=True whitenoise serves static files from the apps.
RUN python manage.py migrate --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--access-logfile", "-", "pygoat.wsgi"]
