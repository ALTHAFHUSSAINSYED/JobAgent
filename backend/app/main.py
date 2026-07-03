import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.correlation import correlation_id_ctx
from app.presentation.routes import router as api_router
from app.infrastructure.redis.event_bus import RedisEventBus
from app.core.metrics import PrometheusMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

logger = logging.getLogger("app.main")

async def redis_subscription_listener(event_bus: RedisEventBus):
    """Background listener for Redis Event Bus events, forwarding them to WebSocket broadcasters."""
    try:
        r = await event_bus.get_redis()
        pubsub = r.pubsub()
        channels = ["config.changed", "resume.loaded", "resume.updated", "system.ready", "health.changed"]
        await pubsub.subscribe(*channels)
        logger.info(f"Redis Event Bus background listener subscribed to: {channels}")
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"].decode("utf-8")
                payload = json.loads(message["data"].decode("utf-8"))
                
                # Import routes broadcast_event dynamically to avoid circular references
                from app.presentation.routes import broadcast_event
                await broadcast_event(channel, payload)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error in Redis subscription listener loop: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle hooks
    setup_logging()
    logger.info("Initializing JobPilot AI backend...")

    # Validate local configuration profile files on startup
    try:
        from app.infrastructure.config.yaml_loader import YAMLConfigLoader
        loader = YAMLConfigLoader()
        loader.validate_profile()
        loader.validate_answers()
        loader.validate_companies()
        logger.info("Successfully validated local configuration profiles (0 errors).")
    except Exception as e:
        logger.error(f"CRITICAL CONFIGURATION ERROR: {e}")
        if settings.ENV == "development":
            raise RuntimeError(f"Startup blocked due to configuration errors: {e}") from e

    # 1. Verify Playwright installation library presence
    try:
        import playwright
        logger.info("Playwright library imported successfully.")
    except ImportError:
        logger.warning("Playwright is NOT installed locally!")

    # Initialize Event Bus
    event_bus = RedisEventBus()
    app.state.event_bus = event_bus

    # 2. Verify Redis connectivity check
    try:
        r = await event_bus.get_redis()
        await r.ping()
        logger.info("Successfully connected to Redis queue.")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")

    # Start background Redis Event Bus subscriber listener daemon task
    listener_task = asyncio.create_task(redis_subscription_listener(event_bus))

    # Publish system.ready event
    await event_bus.publish("system.ready", {
        "timestamp": time.time(),
        "status": "online",
        "version": "0.4.0"
    })

    # Start Config Watcher background checker task
    from app.infrastructure.config.watcher import ConfigWatcher
    watcher = ConfigWatcher()
    
    async def on_config_change(filename: str):
        try:
            # Re-validate changed files
            loader.validate_profile()
            loader.validate_answers()
            loader.validate_companies()
            logger.info(f"Configuration file {filename} modified & successfully reloaded.")
            await event_bus.publish("config.changed", {
                "file": filename,
                "timestamp": time.time(),
                "status": "success"
            })
        except Exception as err:
            logger.error(f"Failed to validate modified configuration file {filename}: {err}")
            await event_bus.publish("config.changed", {
                "file": filename,
                "timestamp": time.time(),
                "status": "error",
                "message": str(err)
            })

    watcher_task = asyncio.create_task(watcher.start(on_config_change))

    yield

    # Shutdown lifecycle hooks
    logger.info("Stopping background tasks and shutting down JobPilot AI backend...")
    watcher.stop()
    watcher_task.cancel()
    listener_task.cancel()
    await event_bus.close()

app = FastAPI(
    title="JobPilot AI Orchestrator API",
    description="Backend controller orchestrator agent endpoints",
    version="0.4.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrometheusMiddleware)

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Set unique correlation tracking ID for incoming request loops
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    token = correlation_id_ctx.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    finally:
        correlation_id_ctx.reset(token)

@app.get("/metrics", tags=["Observability"])
@app.get("/api/v1/metrics", tags=["Observability"])
def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

app.include_router(api_router)
