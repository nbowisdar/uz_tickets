# Telegram Bot Template
This template provides clean start to create bot using aiogram.

## Libraries
- Aiogram
- Aiogram Dialog
- Dishka
- Pydantic
- ~~FastAPI~~ (TODO)
- ~~I18n~~ (TODO)
- SQLAlchemy + asyncpg
- Alembic
- UV
- Ruff
- Docker
- PostgreSQL
- Redis


## Setup with Docker
1. Create `.env.docker` file from `.env.dist` and fill it.
2. Create `password.txt` in `db` folder and fill it.
3. Run docker `docker compose -f compose.yaml -f compose.local.yaml up --build -d`
4. Run migrations with `docker compose exec -it db uv run alembic upgrade head`

## Setup for local start
1. Create `.env.docker` file from `.env.dist` and fill it.
2. Create `password.txt` in `db` folder and fill it.
3. Run `docker compose up --build -d db redis`
4. Install dependencies with `uv sync`
5. Create `.venv` with `uv venv --seed`
6. Activate virtual environment with `source .venv/bin/activate`
7. Run migrations with `alembic upgrade head`
8. Run bot with `python -m bot.main`

## How To?

### Run migrations
```shell
alembic upgrade head
```

### Generate new migration
```shell
alembic revision --autogenerate -m="<migration_name>"
```
