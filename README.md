# 📋 Telegram Bot Template
This template provides clean start to create bot using aiogram.

## 🛠 Stack
- Aiogram
- Aiogram Dialog
- Dishka
- Pydantic
- FastAPI
- ~~I18n~~ (TODO)
- SQLAlchemy + asyncpg
- Alembic
- UV
- Ruff
- Docker
- PostgreSQL
- Redis


## 🐳 Setup with Docker
1. Create `.env` file from `.env.dist` and fill it.
2. Create `password.txt` in `db` folder and fill it.
3. Run docker `docker compose up --build -d`
4. Run migrations with `docker compose exec -it db uv run alembic upgrade head`

## 🐇 Setup for local start
1. Create `.env` file from `.env.dist` and fill it.
2. Create `password.txt` in `db` folder and fill it.
3. Run `docker compose up --build -d db redis`
4. Install dependencies with `uv sync`
5. Create `.venv` with `uv venv --seed`
6. Activate virtual environment with `source .venv/bin/activate`
7. Run migrations with `alembic upgrade head`
8. Run bot with `python -m bot`

## 📎Start with webhook
1. Set USE_WEBHOOK to True in .env
2. Update BOT_SECRET_TOKEN
3. Set API_HOST to your domain
4. Update ORIGINS in .env
5. Start bot with `python -m bot`

## 🍀 For production
`docker compose -f compose.yml -f compose.prod.yml up --build -d`

## How To?

### Run migrations
```shell
alembic upgrade head
```

### Generate new migration
```shell
alembic revision --autogenerate -m="<migration_name>"
```
