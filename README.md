# Online Subscription System for Small Business

B2B / внутрикорпоративный SaaS-инструмент: малый бизнес управляет подписками своих клиентов, тарифными планами, платежами и ролями пользователей.

**Стек:** Python · FastAPI · SQLAlchemy 2.0 · PostgreSQL · JWT · Docker

## Возможности
- Ролевая модель (RBAC): **Admin** / **Employee** / **Customer**
- JWT-аутентификация, хэширование паролей (bcrypt)
- CRUD: тарифы, клиенты, подписки
- Серверная валидация (email, `end_date > start_date`, цена ≥ 0)
- Чистая обработка ошибок: 400 / 401 / 403 / 404 / 422
- Авто-документация Swagger (`/docs`)

## Предварительные требования
- Python 3.12+
- PostgreSQL 16+ (или Docker)
- Git

## Быстрый старт через Docker (рекомендуется)
```bash
cp .env.example .env          # задайте SECRET_KEY (openssl rand -hex 32)
docker compose up --build
# приложение: http://127.0.0.1:8000/docs
```
Наполнение тестовыми данными внутри контейнера:
```bash
docker compose exec web python -m app.seed
```

## Локальный запуск (без Docker)
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # пропишите DATABASE_URL и SECRET_KEY
python -m app.seed
uvicorn app.main:app --reload
```

## Переменные окружения
| Переменная | Назначение |
|---|---|
| `DATABASE_URL` | строка подключения к PostgreSQL |
| `SECRET_KEY` | секрет для подписи JWT (обязательно сменить!) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | время жизни токена |
| `CORS_ORIGINS` | разрешённые домены фронтенда |
| `POSTGRES_USER/PASSWORD/DB` | параметры контейнера БД |

## Тестовые учётные записи (после сидинга)
| Email | Пароль | Роль |
|---|---|---|
| admin@techberry.kz | password123 | admin |
| staff@techberry.kz | password123 | employee |

## Основные эндпоинты
| Метод | Путь | Доступ |
|---|---|---|
| GET | `/health` | публичный |
| GET | `/plans` | публичный |
| POST | `/auth/register` | публичный |
| POST | `/auth/login` | публичный |
| GET/POST/PUT/DELETE | `/customers` | авториз.; delete — admin |
| GET/POST/PUT/DELETE | `/subscriptions` | авториз.; update — admin/employee; delete — admin |
| GET | `/reports/customers/{id}/active-subscriptions` | авториз. (JOIN-запрос) |

## Деплой на Render / Railway
1. Создайте управляемый PostgreSQL, скопируйте его `DATABASE_URL`.
2. Подключите репозиторий; Render соберёт образ по `Dockerfile`.
3. В настройках сервиса задайте переменные окружения (`DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`).
4. Команда запуска: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## Структура проекта
```
app/
├── api/
│   ├── deps.py            # аутентификация и RBAC
│   └── routes/            # health, auth, plans, customers, subscriptions, reports
├── core/security.py       # хэширование паролей + JWT
├── models/                # ORM: company, plan, customer, subscription, user
├── schemas/               # Pydantic-схемы (валидация)
├── config.py              # настройки из .env
├── database.py            # engine + сессии
├── main.py                # точка входа + CORS
└── seed.py                # тестовые данные
docs/                      # схема БД, отчёт, презентация, вопросы защиты
frontend/index.html        # пример интеграции (fetch + CORS)
Dockerfile · docker-compose.yml · requirements.txt
```
