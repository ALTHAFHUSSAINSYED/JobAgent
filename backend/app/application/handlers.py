import logging
import time
from typing import Any, Dict

from app.application.dto import HealthStatusDTO, ConfigurationStatusDTO
from app.application.commands import ValidateConfigurationCommand
from app.application.queries import HealthCheckQuery
from app.domain.interfaces import IEventBus

logger = logging.getLogger("app.application.handlers")

class ValidateConfigurationUseCase:
    def __init__(self, config_parser: Any):
        self.config_parser = config_parser

    async def execute(self, command: ValidateConfigurationCommand) -> ConfigurationStatusDTO:
        """Validates all local config files and profile mappings."""
        try:
            profile_ok = self.config_parser.validate_profile()
            answers_ok = self.config_parser.validate_answers()
            companies_ok = self.config_parser.validate_companies()
            
            return ConfigurationStatusDTO(
                valid=profile_ok and answers_ok and companies_ok,
                profile_loaded=profile_ok,
                answers_loaded=answers_ok,
                companies_loaded=companies_ok
            )
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return ConfigurationStatusDTO(
                valid=False,
                profile_loaded=False,
                answers_loaded=False,
                companies_loaded=False,
                errors=str(e)
            )

class HealthCheckUseCase:
    def __init__(self, db_session: Any, event_bus: IEventBus, config_parser: Any, playwright_verifier: Any, settings_verifier: Any):
        self.db_session = db_session
        self.event_bus = event_bus
        self.config_parser = config_parser
        self.playwright_verifier = playwright_verifier
        self.settings_verifier = settings_verifier

    async def execute(self, query: HealthCheckQuery) -> HealthStatusDTO:
        """Executes operational tests on every structural pillar."""
        # 1. Database Health
        try:
            from sqlalchemy import text
            await self.db_session.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = "unhealthy"

        # 2. Redis Health
        try:
            await self.event_bus.publish("health.ping", {"ping": "pong"})
            redis_status = "healthy"
        except Exception as e:
            logger.error(f"Redis event bus health check failed: {e}")
            redis_status = "unhealthy"

        # 3. Playwright Health
        playwright_ok = self.playwright_verifier.verify()
        playwright_status = "healthy" if playwright_ok else "unhealthy"

        # 4. Configuration Health
        try:
            profile_ok = self.config_parser.validate_profile()
            answers_ok = self.config_parser.validate_answers()
            config_status = "healthy" if (profile_ok and answers_ok) else "unhealthy"
        except Exception:
            config_status = "unhealthy"

        # Overall Status
        overall = "healthy"
        if "unhealthy" in [db_status, redis_status, playwright_status, config_status]:
            overall = "unhealthy"

        return HealthStatusDTO(
            status=overall,
            database=db_status,
            redis=redis_status,
            playwright=playwright_status,
            configuration=config_status
        )
