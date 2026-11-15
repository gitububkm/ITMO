# URL Shortener API (DevSecOps Labs 2–3)

Backend URL shortener with JWT auth, Redis cache, Celery click analytics, GitLab CI and SonarQube SAST.

## Stack

- **FastAPI** — REST API
- **PostgreSQL** + Alembic — storage and migrations
- **Redis** — link cache + refresh tokens + Celery broker
- **Celery** — async click recording, expired links cleanup
- **Docker Compose** — local/runtime environment
- **GitLab CI** — `linter` → `build` → `sast` → `tests`
- **SonarQube Community Build** — SAST

## Quick start

```bash
cp .env.example .env
cd backend
poetry config virtualenvs.in-project true
poetry env use 3.13
poetry install --with dev
cd ..
docker compose up -d --build
```

API docs: http://127.0.0.1:8000/docs
Health: http://127.0.0.1:8000/health

Pre-commit (from repo root):

```bash
pipx install pre-commit
pre-commit install
pre-commit run --all-files
```

## Main endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register |
| POST | `/api/v1/auth/login` | Login (form: username=email, password) |
| POST | `/api/v1/auth/refresh` | Refresh tokens |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/links` | Create short link |
| GET | `/api/v1/links` | List own links |
| GET | `/api/v1/links/{id}/stats` | Click stats |
| DELETE | `/api/v1/links/{id}` | Deactivate link |
| GET | `/r/{short_code}` | Redirect + enqueue click |

## Tests

Requires Postgres/Redis from `docker compose up -d` (or full stack).

```bash
cd backend
set -a && source ../.env && set +a
poetry run pytest
```

## GitLab CI jobs

1. **linter** — poetry install + pre-commit (ruff, mypy, gitleaks)
2. **build** — `docker compose build`
3. **sast** — SonarQube analysis via `pysonar` (after `build`, before deploy); fails when the quality gate fails
4. **tests** — compose up + pytest

Pipelines run for every branch push and for merge requests.

## SAST: SonarQube Community Build

The team shares one SonarQube Community Build server running on the GitLab host (port 9000);
every member has their own private project. The `DevSecOps` quality gate fails on any vulnerability
or unreviewed security hotspot in the whole code, which makes the `sast` job fail.

CI/CD variables (GitLab → Settings → CI/CD → Variables):

- `SONAR_TOKEN` (masked, not protected) — analysis token for the `devsecops-linkshortener` project;
- `SONAR_HOST_URL` (optional) — defaults to `http://host.docker.internal:9000` (the runner's host).

Analysis settings live in `sonar-project.properties`. Results: `http://ame-gitlab:9000/dashboard?id=devsecops-linkshortener`.

## Architecture

```
Client → FastAPI
          ├─ PostgreSQL (users, links, clicks)
          ├─ Redis (cache + refresh tokens)
          └─ Celery worker (record clicks, expire links)
```
