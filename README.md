# shortlinks

[![CI](https://github.com/SyrymAbdikhan/shortlinks/actions/workflows/ci.yml/badge.svg)](https://github.com/SyrymAbdikhan/shortlinks/actions/workflows/ci.yml)
[![CD](https://github.com/SyrymAbdikhan/shortlinks/actions/workflows/cd.yml/badge.svg)](https://github.com/SyrymAbdikhan/shortlinks/actions/workflows/cd.yml)

Minimal URL shortener REST API built with FastAPI, PostgreSQL, and Docker.

## Stack

- **FastAPI** — async web framework
- **SQLAlchemy + asyncpg** — async ORM + PostgreSQL driver
- **Pydantic** — request/response validation
- **uv** — package management
- **Docker + Compose** — containerised runtime
- **pytest + pytest-asyncio** — test suite
- **ruff** — linting and formatting

## Quick start

```bash
cp .env.example .env
# edit .env — set an API_KEY
make run
```

The API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## Environment variables

| Variable            | Description                    | Default      |
| ------------------- | ------------------------------ | ------------ |
| `POSTGRES_USER`     | Database username              | `postgres`   |
| `POSTGRES_PASSWORD` | Database password              | `postgres`   |
| `POSTGRES_DB`       | Database name                  | `shortlinks` |
| `API_KEY`           | Static key for write endpoints | —            |

`DATABASE_URL` is assembled automatically from the above vars in `docker-compose.yml`.  
For local development without Docker, set it manually:

```bash
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/shortlinks
```

**Generate an API key**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## API endpoints

### Create a short link

```bash
curl -X POST http://localhost:8000/links \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://example.com/some/long/path"}'
```

```json
{
  "code": "aB3xYz",
  "url": "https://example.com/some/long/path",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Redirect

```bash
curl -L http://localhost:8000/aB3xYz
```

### List all links

```bash
curl http://localhost:8000/links
```

### Delete a link

```bash
curl -X DELETE http://localhost:8000/links/aB3xYz \
  -H "X-API-Key: your-api-key"
```

### Health check

```bash
curl http://localhost:8000/health
```

## Auth

Write endpoints (`POST /links`, `DELETE /links/{code}`) require `X-API-Key` header.

| Situation      | Status |
| -------------- | ------ |
| Header missing | `403`  |
| Wrong key      | `401`  |

Read endpoints are public.

## Development

```bash
uv sync          # create .venv and install all deps
make test        # run test suite
make lint        # check with ruff
make format      # auto-fix formatting
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for VPS setup and CI/CD configuration.

## Project structure

```
app/
├── api/
│   ├── deps.py          # shared dependencies
│   ├── main.py          # top-level api_router
│   └── routes/
│       ├── health.py    # GET /health
│       └── links.py     # all /links endpoints
├── core/
│   ├── config.py        # settings (pydantic-settings)
│   ├── db.py            # async engine + Base
│   └── security.py      # X-API-Key verification
├── crud.py              # async DB operations
├── models.py            # SQLAlchemy ORM model
├── schemas.py           # Pydantic request/response schemas
└── main.py              # FastAPI app
tests/
├── conftest.py          # fixtures
└── test_links.py        # tests
```
