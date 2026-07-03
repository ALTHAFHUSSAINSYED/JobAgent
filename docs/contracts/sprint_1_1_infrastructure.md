# Sprint 1.1: Infrastructure & Docker Compose Setup

This contract specifies the deployment and runtime container orchestration setup for JobPilot AI.

---

## 1. Goal
Configure the complete multi-container Docker environment (FastAPI Backend, React Frontend, PostgreSQL 17, Redis 7, pgAdmin 4) with isolated bridge networks, health checks, persistent volumes, and secure local environment mapping.

---

## 2. Directory Layout & Key Files
The following infrastructure files must be created or configured:

```text
JobPilot/
├── docker-compose.yml           # Multi-service runtime orchestrator
├── .env.example                 # Reference environment variables schema
├── .env                         # Local git-ignored secrets
├── backend/
│   └── Dockerfile               # Backend python container recipe
└── frontend/
    └── Dockerfile               # Frontend React container recipe
```

---

## 3. Specifications

### 3.1 `docker-compose.yml`
```yaml
version: '3.8'

networks:
  jobpilot_net:
    driver: bridge

volumes:
  postgres_data:
  redis_data:

services:
  postgres:
    image: postgres:17-alpine
    container_name: jobpilot_postgres
    restart: always
    environment:
      POSTGRES_DB: jobpilot_db
      POSTGRES_USER: jobpilot_user
      POSTGRES_PASSWORD: jobpilot_secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - jobpilot_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jobpilot_user -d jobpilot_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: jobpilot_redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - jobpilot_net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: jobpilot_pgadmin
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@jobpilot.local
      PGADMIN_DEFAULT_PASSWORD: admin_secure_password
    ports:
      - "5050:80"
    networks:
      - jobpilot_net
    depends_on:
      postgres:
        condition: service_healthy

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: jobpilot_backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://jobpilot_user:jobpilot_secure_password@postgres:5432/jobpilot_db
      - REDIS_URL=redis://redis:6379/0
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - ENV=production
    volumes:
      - ./config:/app/config
      - ./resumes:/app/resumes
      - ./logs:/app/logs
    networks:
      - jobpilot_net
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: jobpilot_frontend
    restart: always
    ports:
      - "3000:3000"
    networks:
      - jobpilot_net
    depends_on:
      - backend
```

### 3.2 `backend/Dockerfile`
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system utilities & curl for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and CLI dependencies
RUN playwright install-deps chromium
RUN playwright install chromium

COPY . .

# Expose port and launch server
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.3 `frontend/Dockerfile`
```dockerfile
# Build stage
FROM node:22-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM node:22-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

---

## 4. Acceptance Criteria
- Running `docker compose up -d` successfully spins up all 5 containers.
- All container healthchecks return `healthy`.
- pgAdmin UI is accessible at `http://localhost:5050` with login `admin@jobpilot.local`.
- Postgres can be connected inside pgAdmin using the internal hostname `postgres` and port `5432`.
