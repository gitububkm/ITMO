# Документация по авторизации и ролевой модели

## Обзор

API использует JWT токены для авторизации с поддержкой refresh токенов и OAuth через GitHub.

## Ролевая модель

### Роли пользователей

#### 1. **USER** (Обычный пользователь)
- **Доступ:**
  - Просмотр новостей и комментариев (GET)
  - Создание комментариев
  - Редактирование и удаление своих комментариев
- **Ограничения:**
  - Не может создавать новости
  - Не может редактировать чужие комментарии

#### 2. **AUTHOR** (Верифицированный автор)
- **Доступ:**
  - Все права обычного пользователя
  - Создание новостей
  - Редактирование и удаление своих новостей
- **Ограничения:**
  - Не может редактировать чужие новости

#### 3. **ADMIN** (Администратор)
- **Доступ:**
  - Все операции над всеми сущностями
  - Управление пользователями (CRUD)
  - Редактирование и удаление любых новостей и комментариев
- **Без ограничений**

## Аутентификация

### 1. Регистрация по email/паролю

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "password": "secure_password123"
}
```

**Response:** JWT токены
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Особенности:**
- Новый пользователь получает роль `USER` по умолчанию
- Автоматически создается refresh session с User-Agent

### 2. Вход по email/паролю

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "ivan@example.com",
  "password": "secure_password123"
}
```

**Response:** JWT токены (аналогично регистрации)

### 3. GitHub OAuth

**Flow:**

1. **Инициация авторизации**
   - Endpoint: `GET /auth/github/login`
   - Перенаправляет на GitHub для авторизации

2. **Callback**
   - Endpoint: `GET /auth/github/callback?code=...`
   - Получает данные пользователя от GitHub
   - Создает или находит пользователя по `github_id`
   - Возвращает JWT токены

**Особенности:**
- Если пользователь с таким email уже существует, привязывает `github_id`
- Новый пользователь через GitHub получает роль `USER`
- Пароль не требуется

## JWT Токены

### Access Token

- **Срок жизни:** 30 минут
- **Назначение:** Доступ к защищенным эндпоинтам
- **Передача:** HTTP Header `Authorization: Bearer <token>`
- **Payload:**
  ```json
  {
    "sub": "user_id",
    "exp": 1234567890,
    "type": "access"
  }
  ```

### Refresh Token

- **Срок жизни:** 30 дней
- **Назначение:** Обновление access токена
- **Хранение:** В таблице `refresh_sessions` с метаданными
- **Payload:**
  ```json
  {
    "sub": "user_id",
    "exp": 1234567890,
    "type": "refresh"
  }
  ```

### Обновление токенов

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** Новая пара токенов

**Процесс:**
1. Проверка refresh токена в БД
2. Проверка срока действия
3. Удаление старой сессии
4. Создание новой пары токенов

## Управление сессиями

### Просмотр активных сессий

**Endpoint:** `GET /auth/sessions`

**Response:**
```json
[
  {
    "id": 1,
    "user_agent": "Mozilla/5.0...",
    "created_at": "2024-10-16T10:00:00",
    "expires_at": "2024-11-15T10:00:00"
  }
]
```

### Выход (Logout)

**Endpoint:** `POST /auth/logout`

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

- Удаляет конкретную сессию из БД
- Access токен остается действительным до истечения срока

### Выход из всех сессий

**Endpoint:** `DELETE /auth/sessions`

- Удаляет все refresh сессии пользователя
- Требует авторизации (access токен)

## Получение информации о себе

**Endpoint:** `GET /auth/me`

**Response:**
```json
{
  "id": 1,
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "role": "AUTHOR",
  "is_verified_author": true,
  "avatar": "https://...",
  "registration_date": "2024-10-16T10:00:00"
}
```

## Защита эндпоинтов

### Dependencies

#### `get_current_user`
- Проверяет наличие и валидность access токена
- Возвращает объект User
- Используется для всех защищенных эндпоинтов

#### `get_current_verified_author`
- Проверяет, что пользователь - автор или админ
- Используется для создания новостей

#### `get_current_admin`
- Проверяет, что пользователь - админ
- Используется для управления пользователями

#### `get_news_with_permission`
- Проверяет права на редактирование новости
- Разрешает автору новости или админу

#### `get_comment_with_permission`
- Проверяет права на редактирование комментария
- Разрешает автору комментария или админу

#### `get_optional_current_user`
- Не требует авторизации, но извлекает пользователя если токен есть
- Используется для публичных эндпоинтов (GET)

## Примеры использования

### 1. Регистрация и создание новости

```bash
# Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Автор","email":"author@test.com","password":"pass123"}'

# Получаем access_token из ответа

# Попытка создать новость (не получится - не автор)
curl -X POST http://localhost:8000/news/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Новость","content":{"body":"Текст"}}'
# Ответ: 403 Forbidden

# Админ должен сделать пользователя автором через БД или эндпоинт
```

### 2. Создание комментария

```bash
# Любой авторизованный пользователь может комментировать
curl -X POST http://localhost:8000/comments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Отличная новость!","news_id":1}'
```

### 3. Обновление refresh токена

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```