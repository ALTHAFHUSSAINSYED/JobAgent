from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_async_session
from app.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from app.infrastructure.repositories.candidate import SQLAlchemyCandidateRepository
from app.infrastructure.repositories.job import SQLAlchemyJobRepository
from app.infrastructure.repositories.application import SQLAlchemyApplicationRepository
from app.infrastructure.redis.event_bus import RedisEventBus
from app.infrastructure.config.yaml_loader import YAMLConfigLoader
from app.infrastructure.browser_client import PlaywrightVerifier
from app.infrastructure.llm_client import OpenRouterVerifier
from app.application.handlers import HealthCheckUseCase, ValidateConfigurationUseCase

def get_yaml_config_loader() -> YAMLConfigLoader:
    return YAMLConfigLoader()

def get_event_bus() -> RedisEventBus:
    return RedisEventBus()

def get_playwright_verifier() -> PlaywrightVerifier:
    return PlaywrightVerifier()

def get_openrouter_verifier() -> OpenRouterVerifier:
    return OpenRouterVerifier()

def get_unit_of_work(session: AsyncSession = Depends(get_async_session)) -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(session)

def get_candidate_repository(session: AsyncSession = Depends(get_async_session)) -> SQLAlchemyCandidateRepository:
    return SQLAlchemyCandidateRepository(session)

def get_job_repository(session: AsyncSession = Depends(get_async_session)) -> SQLAlchemyJobRepository:
    return SQLAlchemyJobRepository(session)

def get_application_repository(session: AsyncSession = Depends(get_async_session)) -> SQLAlchemyApplicationRepository:
    return SQLAlchemyApplicationRepository(session)

def get_health_check_use_case(
    session: AsyncSession = Depends(get_async_session),
    event_bus: RedisEventBus = Depends(get_event_bus),
    config_loader: YAMLConfigLoader = Depends(get_yaml_config_loader),
    playwright_verifier: PlaywrightVerifier = Depends(get_playwright_verifier),
    openrouter_verifier: OpenRouterVerifier = Depends(get_openrouter_verifier)
) -> HealthCheckUseCase:
    return HealthCheckUseCase(
        db_session=session,
        event_bus=event_bus,
        config_parser=config_loader,
        playwright_verifier=playwright_verifier,
        settings_verifier=openrouter_verifier
    )

def get_validate_config_use_case(
    config_loader: YAMLConfigLoader = Depends(get_yaml_config_loader)
) -> ValidateConfigurationUseCase:
    return ValidateConfigurationUseCase(config_loader)
