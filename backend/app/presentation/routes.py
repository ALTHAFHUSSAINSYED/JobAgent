import asyncio
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

router = APIRouter()

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
    """Fetches high level summary overview metrics and counts."""
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
    
    # Establish local queue block
    queue = asyncio.Queue()
    active_connections.append(queue)
    
    try:
        # Populate history logs
        for log_line in list(log_history):
            await websocket.send_text(log_line)
            
        while True:
            # Yield new line messages
            log_line = await queue.get()
            await websocket.send_text(log_line)
    except WebSocketDisconnect:
        pass
    finally:
        if queue in active_connections:
            active_connections.remove(queue)
