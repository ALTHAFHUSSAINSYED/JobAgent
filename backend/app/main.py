import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.correlation import correlation_id_ctx
from app.presentation.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle hooks
    setup_logging()
    logger = logging.getLogger("app.main")
    logger.info("Initializing JobPilot AI backend...")

    # 1. Verify Playwright installation library presence
    try:
        import playwright
        logger.info("Playwright library imported successfully.")
    except ImportError:
        logger.warning("Playwright is NOT installed locally!")

    # 2. Verify Redis connectivity check
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        logger.info("Successfully connected to Redis queue.")
        await r.close()
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {e}")

    yield
    # Shutdown lifecycle hooks
    logger.info("Shutting down JobPilot AI backend...")

app = FastAPI(
    title="JobPilot AI API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation ID tracing middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = correlation_id_ctx.set(corr_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = corr_id
        return response
    finally:
        correlation_id_ctx.reset(token)

# Register routers
app.include_router(api_router)
