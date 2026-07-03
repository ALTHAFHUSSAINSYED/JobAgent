import pytest
import asyncio
from app.infrastructure.database import async_engine

@pytest.fixture(scope="session")
def event_loop():
    """Create a single session-wide event loop for running all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def cleanup_database_engine():
    """Dispose engine after all tests to cleanly close pool connections."""
    yield
    await async_engine.dispose()
