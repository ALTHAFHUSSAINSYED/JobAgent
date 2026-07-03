from fastapi import APIRouter, Depends
from app.application.dto import HealthStatusDTO, ConfigurationStatusDTO
from app.application.queries import HealthCheckQuery
from app.application.commands import ValidateConfigurationCommand
from app.infrastructure.providers.dependencies import (
    get_health_check_use_case,
    get_validate_config_use_case
)
from app.application.handlers import HealthCheckUseCase, ValidateConfigurationUseCase

router = APIRouter()

@router.get("/health", response_model=HealthStatusDTO, tags=["Health"])
@router.get("/api/v1/health", response_model=HealthStatusDTO, tags=["Health"])
async def health_check(
    use_case: HealthCheckUseCase = Depends(get_health_check_use_case)
):
    """Diagnostics checks for database, cache, Playwright, and local configuration profile files."""
    query = HealthCheckQuery()
    return await use_case.execute(query)

@router.post("/api/v1/config/validate", response_model=ConfigurationStatusDTO, tags=["Configuration"])
async def validate_configuration(
    use_case: ValidateConfigurationUseCase = Depends(get_validate_config_use_case)
):
    """Checks YAML configurations and candidate profiles."""
    command = ValidateConfigurationCommand()
    return await use_case.execute(command)
