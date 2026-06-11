# Deployment

The CD workflow builds and pushes the Docker image to GHCR on every push to `main`, then SSHs into the VPS and redeploys.

## GitHub secrets

Add these in Settings → Secrets and variables → Actions:

| Secret       | Description                                                     |
| ------------ | --------------------------------------------------------------- |
| `GHCR_TOKEN` | GitHub PAT with `write:packages` scope                          |
| `SSH_HOST`   | VPS IP or hostname                                              |
| `SSH_USER`   | SSH login user                                                  |
| `SSH_KEY`    | Private key (full `-----BEGIN OPENSSH PRIVATE KEY-----` block)  |

## VPS setup

[Install Docker](https://docs.docker.com/engine/install/) on the VPS, then create `~/shortlinks/` with these three files:

**`docker-compose.yml`**
```yaml
services:
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    container_name: shortlinks-db
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-shortlinks}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-shortlinks}"]
      interval: 5s
      timeout: 5s
      retries: 3

  app:
    image: ghcr.io/syrymabdikhan/shortlinks:latest
    restart: unless-stopped
    expose:
      - "8000"
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@shortlinks-db:5432/${POSTGRES_DB:-shortlinks}
    healthcheck:
      test: ["CMD-SHELL", "wget -qO /dev/null http://127.0.0.1:8000/health"]
      interval: 5s
      timeout: 5s
      retries: 3
      start_period: 30s
    depends_on:
      db:
        condition: service_healthy

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 5s
      timeout: 5s
      retries: 3
    depends_on:
      - app

volumes:
  postgres_data:
```

**`nginx.conf`**
```nginx
server {
    listen 80;

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**`.env`**
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=shortlinks
API_KEY=yourapikey
```

## First deploy

Push to `main` to "build and push" the image and deploy automatically,
or deploy manually:

```bash
cd ~/shortlinks
docker compose up -d
```

