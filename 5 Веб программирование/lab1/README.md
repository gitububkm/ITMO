# lab1_Bardyshev_A_A

CRUD API для управления пользователями, новостями и комментариями, построенный на FastAPI, SQLAlchemy и PostgreSQL.


## Авторизация

Приложение теперь поддерживает:
- **JWT токены** (access + refresh)
- **GitHub OAuth**
- **Ролевую модель** (USER, AUTHOR, ADMIN)
- **Управление сессиями**

Подробная документация: **[docs/auth.md](docs/auth.md)**

## Описание проекта

API сервис предоставляет полный функционал CRUD операций для трех основных сущностей:
- **Пользователи** - управление пользователями системы
- **Новости** - публикация и управление новостями (доступно только верифицированным авторам)
- **Комментарии** - комментирование новостей

## Модели данных

### User (Пользователь)
- `id` - уникальный идентификатор
- `name` - имя пользователя
- `email` - email (уникальный)
- `registration_date` - дата регистрации
- `is_verified_author` - статус верификации как автора
- `avatar` - URL аватарки

### News (Новость)
- `id` - уникальный идентификатор
- `title` - заголовок новости
- `content` - содержание в JSON формате
- `publication_date` - дата публикации
- `author_id` - ID автора (связь с User)
- `cover` - URL обложки

### Comment (Комментарий)
- `id` - уникальный идентификатор
- `text` - текст комментария
- `news_id` - ID новости (связь с News)
- `author_id` - ID автора (связь с User)
- `publication_date` - дата публикации


## Требования

- Python 3.10+
- PostgreSQL 12+

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/itmo-webdev/lab1_Bardyshev_A_A.git
cd lab1_Bardyshev_A_A
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
```

Активация:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных


```bash
docker-compose up -d
```

Это запустит PostgreSQL на порту 5432 с настройками из docker-compose.yml.


### 5. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте подключение к БД:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/news_db
```

### 6. Применение миграций

```bash
alembic upgrade head
```

Это создаст все таблицы и добавит моковые данные.

### 7. Запуск приложения

```bash
python main.py
```

Или через uvicorn напрямую:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: http://localhost:8000

API документация (Swagger): http://localhost:8000/docs

## Миграции

### Структура миграций

1. **001_initial_migration.py** - Создание таблиц для всех моделей
2. **002_add_mock_data.py** - Добавление тестовых данных

### Команды Alembic

```bash
alembic revision --autogenerate -m "описание миграции"
alembic upgrade head
alembic downgrade -1
alembic current
alembic history
```

## Примеры использования API

### Пользователи

#### Создание пользователя

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Бардышев Артём",
    "email": "ububkmart@gmail.com",
    "is_verified_author": true,
    "avatar": "https://example.com/avatar.jpg"
  }'
```

Ответ:
```json
{
  "id": 4,
  "name": "Артём Бардышев",
  "email": "ububkmart@gmail.com",
  "registration_date": "2024-01-01T12:00:00",
  "is_verified_author": true,
  "avatar": "https://example.com/avatar.jpg"
}
```

#### Получение всех пользователей

```bash
curl -X GET "http://localhost:8000/users/"
```

#### Получение пользователя по ID

```bash
curl -X GET "http://localhost:8000/users/1"
```

#### Обновление пользователя

```bash
curl -X PUT "http://localhost:8000/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван Иванович Иванов",
    "is_verified_author": true
  }'
```

#### Удаление пользователя

```bash
curl -X DELETE "http://localhost:8000/users/3"
```

### Новости

#### Создание новости (только для верифицированных авторов)

```bash
curl -X POST "http://localhost:8000/news/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новая технология в веб-разработке",
    "content": {
      "type": "article",
      "body": "Описание новой технологии",
      "tags": ["технологии", "веб"]
    },
    "author_id": 1,
    "cover": "https://example.com/cover.jpg"
  }'
```

Ответ:
```json
{
  "id": 3,
  "title": "Новая технология в веб-разработке",
  "content": {
    "type": "article",
    "body": "Описание новой технологии",
    "tags": ["технологии", "веб"]
  },
  "publication_date": "2024-01-01T12:00:00",
  "author_id": 1,
  "cover": "https://example.com/cover.jpg"
}
```

#### Получение всех новостей

```bash
curl -X GET "http://localhost:8000/news/"
```

#### Получение новости по ID

```bash
curl -X GET "http://localhost:8000/news/1"
```

#### Обновление новости

```bash
curl -X PUT "http://localhost:8000/news/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Обновленный заголовок",
    "content": {
      "type": "article",
      "body": "Обновленное содержание"
    }
  }'
```

#### Удаление новости (удаляет все связанные комментарии)

```bash
curl -X DELETE "http://localhost:8000/news/1"
```

### Комментарии

#### Создание комментария

```bash
curl -X POST "http://localhost:8000/comments/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Отличная статья!",
    "news_id": 1,
    "author_id": 2
  }'
```

Ответ:
```json
{
  "id": 4,
  "text": "Отличная статья!",
  "news_id": 1,
  "author_id": 2,
  "publication_date": "2024-01-01T12:00:00"
}
```

#### Получение всех комментариев

```bash
curl -X GET "http://localhost:8000/comments/"
```

#### Получение комментариев к конкретной новости

```bash
curl -X GET "http://localhost:8000/comments/news/1"
```

#### Получение комментария по ID

```bash
curl -X GET "http://localhost:8000/comments/1"
```

#### Обновление комментария

```bash
curl -X PUT "http://localhost:8000/comments/1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Обновленный текст комментария"
  }'
```

#### Удаление комментария

```bash
curl -X DELETE "http://localhost:8000/comments/1"
```

## Сценарий использования

### Полный тестовый сценарий

```bash
# 1. Создание пользователей
curl -X POST "http://localhost:8000/users/" -H "Content-Type: application/json" \
  -d '{"name": "Автор 1", "email": "author1@example.com", "is_verified_author": true}'

curl -X POST "http://localhost:8000/users/" -H "Content-Type: application/json" \
  -d '{"name": "Читатель 1", "email": "reader1@example.com", "is_verified_author": false}'

# 2. Создание новости от верифицированного автора
curl -X POST "http://localhost:8000/news/" -H "Content-Type: application/json" \
  -d '{"title": "Тестовая новость", "content": {"body": "Содержание"}, "author_id": 1}'

# 3. Создание комментария от другого пользователя
curl -X POST "http://localhost:8000/comments/" -H "Content-Type: application/json" \
  -d '{"text": "Интересная новость!", "news_id": 1, "author_id": 2}'

# 4. Изменение новости
curl -X PUT "http://localhost:8000/news/1" -H "Content-Type: application/json" \
  -d '{"title": "Обновленная новость"}'

# 5. Изменение комментария
curl -X PUT "http://localhost:8000/comments/1" -H "Content-Type: application/json" \
  -d '{"text": "Обновленный комментарий"}'

# 6. Удаление новости вместе со всеми комментариями
curl -X DELETE "http://localhost:8000/news/1"
```

## Тестирование

Для тестирования всех эндпоинтов можно использовать:
- Встроенный Swagger UI: http://localhost:8000/docs
- ReDoc документацию: http://localhost:8000/redoc
- Postman или аналогичные инструменты
- curl команды (примеры выше)

## Фоновые уведомления (Celery)

Добавлено мок-уведомление пользователей о новых новостях и еженедельный дайджест (в лог-файл вместо email) на Celery + Redis.

### Переменные окружения (опционально)

```
# Брокер и бэкенд Celery (по умолчанию redis://localhost:6379/{1,2})
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
REDIS_URL=redis://localhost:6379
CELERY_TIMEZONE=Europe/Moscow
```

### Запуск инфраструктуры

- Redis (если не установлен):
  - Docker: `docker run -p 6379:6379 --name redis -d redis:7`

### Запуск приложения и воркеров

1) Приложение API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2) Celery worker:

```bash
# Windows: обязательно одиночный пул
celery -A src.celery_app.celery_app worker -P solo -l info

# Linux/Mac:
# celery -A src.celery_app.celery_app worker -l info
```

3) Celery beat (расписание еженедельного дайджеста по воскресеньям 09:00):

```bash
celery -A src.celery_app.celery_app beat -l info
```

### Как это работает

- При создании новости через `POST /news/` ставится задача `notify_new_news(news_id)`.
- Каждое воскресенье в 09:00 запускается `send_weekly_digest()`.
- Оба задания логируют «отправленные письма» в файл `logs/notifications.log`.
- Настроены ретраи с backoff и идемпотентность через Redis-ключи.

## Frontend (React + Vite)

Для выполнения пункта 5 ТЗ добавлен отдельный клиент в папке `../front/`, созданный через `npm create vite@latest` (React + TypeScript).

### Возможности интерфейса
- Главная страница (`/`) запрашивает `GET /news` и показывает ленту. Верифицированные авторы и администраторы могут создавать новости (POST `/news`).
- Страница новости (`/news/:id`) подгружает `GET /news/{id}` и `GET /comments/news/{id}`, позволяет:
  - Добавлять комментарии (POST `/comments`);
  - Редактировать и удалять свои комментарии (PUT/DELETE `/comments/{id}`);
  - Редактировать и удалять новость при наличии прав (PUT/DELETE `/news/{id}`).
- Страница авторизации (`/auth`) содержит формы входа и регистрации (POST `/auth/login`, `/auth/register`), отображает текущего пользователя (`GET /auth/me`) и активные refresh-сессии (`GET /auth/sessions`), позволяет завершить все сессии (`DELETE /auth/sessions`). Все запросы выполняются через `axios`, токены автоматически подставляются и обновляются.

Видимость кнопок зависит от роли пользователя и флага `is_verified_author`, получаемых из API.

### Запуск фронтенда локально
```bash
cd ../front
npm install          # установка зависимостей
# создайте .env со строкой VITE_API_URL=http://localhost:8000 (или своим адресом API)
npm run dev          # старт дев-сервера на http://localhost:5173
```

Доступные команды:
- `npm run dev` — запуск в режиме разработки;
- `npm run build` — production-сборка;
- `npm run preview` — предпросмотр собранной версии.

### Публикация
По требованию ЛР5 фронтенд необходимо вынести в отдельный приватный репозиторий организации `itmo-webdev` (например, `lab5_Bardyshev_A_A`). Текущая директория `../front/` автономна: её достаточно скопировать в новый репозиторий вместе с инструкциями выше.

## Автор

Бардышев А.А.
