import asyncio
import json
import logging
import time
from typing import List
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.application.dto import (
    HealthStatusDTO,
    ConfigurationStatusDTO,
    SystemInfoDTO,
    ConfigDetailDTO,
    DashboardDTO,
    VersionDTO
)
from app.application.queries import (
    HealthCheckQuery,
    GetSystemInfoQuery,
    GetConfigurationDetailsQuery,
    GetDashboardDataQuery,
    GetVersionQuery
)
from app.application.commands import ValidateConfigurationCommand
from app.infrastructure.providers.dependencies import (
    get_health_check_use_case,
    get_validate_config_use_case,
    get_system_info_use_case,
    get_configuration_details_use_case,
    get_dashboard_data_use_case,
    get_version_use_case
)
from app.application.handlers import (
    HealthCheckUseCase,
    ValidateConfigurationUseCase,
    GetSystemInfoUseCase,
    GetConfigurationDetailsUseCase,
    GetDashboardDataUseCase,
    GetVersionUseCase
)
from app.core.logging import active_connections, log_history

logger = logging.getLogger("app.presentation.routes")
router = APIRouter()

# WebSocket connections tracking lists
events_connections: List[WebSocket] = []

async def broadcast_event(event_name: str, payload: dict):
    """Broadcasts Redis Event Bus notifications to active WebSocket event subscribers."""
    message = json.dumps({"event": event_name, "payload": payload})
    for ws in list(events_connections):
        try:
            await ws.send_text(message)
        except Exception:
            if ws in events_connections:
                events_connections.remove(ws)

@router.get("/health", response_model=HealthStatusDTO, tags=["Health"])
@router.get("/api/v1/health", response_model=HealthStatusDTO, tags=["Health"])
async def health_check(
    use_case: HealthCheckUseCase = Depends(get_health_check_use_case)
):
    """Heartbeat check with expanded backend component states details."""
    query = HealthCheckQuery()
    return await use_case.execute(query)

@router.post("/api/v1/config/validate", response_model=ConfigurationStatusDTO, tags=["Configuration"])
async def validate_configuration(
    use_case: ValidateConfigurationUseCase = Depends(get_validate_config_use_case)
):
    """Triggers validation checks on credentials and YAML profile schema variables."""
    command = ValidateConfigurationCommand()
    return await use_case.execute(command)

@router.get("/api/v1/dashboard", response_model=DashboardDTO, tags=["Dashboard"])
async def get_dashboard(
    use_case: GetDashboardDataUseCase = Depends(get_dashboard_data_use_case)
):
    """Fetches high level summary overview metrics, counts, and scanned resumes."""
    query = GetDashboardDataQuery()
    return await use_case.execute(query)

@router.get("/api/v1/system/info", response_model=SystemInfoDTO, tags=["Admin"])
async def get_system_info(
    use_case: GetSystemInfoUseCase = Depends(get_system_info_use_case)
):
    """Fetches runtime dependencies, platform details, and active Git commits hashes."""
    query = GetSystemInfoQuery()
    return await use_case.execute(query)

@router.get("/api/v1/configuration", response_model=ConfigDetailDTO, tags=["Configuration"])
async def get_configuration(
    use_case: GetConfigurationDetailsUseCase = Depends(get_configuration_details_use_case)
):
    """Retrieves parsed expected salary range and target professional experience CTC settings."""
    query = GetConfigurationDetailsQuery()
    return await use_case.execute(query)

@router.get("/api/v1/version", response_model=VersionDTO, tags=["Admin"])
async def get_version(
    use_case: GetVersionUseCase = Depends(get_version_use_case)
):
    """Exposes release build version metadata details."""
    query = GetVersionQuery()
    return await use_case.execute(query)

@router.get("/api/v1/logs", response_model=List[str], tags=["Admin"])
async def get_recent_logs():
    """Retrieves standard in-memory stored log histories."""
    return list(log_history)

@router.websocket("/api/v1/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """Live stream connection broadcast pipeline streaming JSON logs records to React terminal views."""
    await websocket.accept()
    queue = asyncio.Queue()
    active_connections.append(queue)
    try:
        # Re-push cached history logs
        for log_line in list(log_history):
            await websocket.send_text(log_line)
            
        while True:
            log_line = await queue.get()
            await websocket.send_text(log_line)
    except WebSocketDisconnect:
        pass
    finally:
        if queue in active_connections:
            active_connections.remove(queue)

@router.websocket("/api/v1/ws/events")
async def websocket_events(websocket: WebSocket):
    """Listens for custom backend system state and config change notifications."""
    await websocket.accept()
    events_connections.append(websocket)
    try:
        while True:
            # Hold socket connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in events_connections:
            events_connections.remove(websocket)

@router.websocket("/api/v1/ws/system")
async def websocket_system(
    websocket: WebSocket,
    use_case: GetSystemInfoUseCase = Depends(get_system_info_use_case),
    dashboard_use_case: GetDashboardDataUseCase = Depends(get_dashboard_data_use_case)
):
    """Streams system metrics, latency diagnostics, and pool sizes every 4 seconds."""
    await websocket.accept()
    try:
        while True:
            sys_info = await use_case.execute(GetSystemInfoQuery())
            dash_data = await dashboard_use_case.execute(GetDashboardDataQuery())
            
            payload = {
                "system": sys_info.model_dump(),
                "latencies": dash_data.latencies,
                "database_pool": dash_data.database_pool,
                "playwright_details": dash_data.playwright_details,
                "timestamp": time.time()
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(4.0)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Error in websocket system stats stream: {e}")
