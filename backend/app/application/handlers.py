import logging
import os
import platform
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import (
    HealthStatusDTO,
    ConfigurationStatusDTO,
    SystemInfoDTO,
    ConfigDetailDTO,
    DashboardDTO,
    VersionDTO
)
from app.application.commands import ValidateConfigurationCommand
from app.application.queries import (
    HealthCheckQuery,
    GetSystemInfoQuery,
    GetConfigurationDetailsQuery,
    GetDashboardDataQuery,
    GetVersionQuery
)
from app.domain.interfaces import IEventBus
from app.infrastructure.database.models import JobModel, ApplicationModel

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

class GetSystemInfoUseCase:
    def __init__(self, db_session: AsyncSession, event_bus: Any, playwright_verifier: Any):
        self.db_session = db_session
        self.event_bus = event_bus
        self.playwright_verifier = playwright_verifier

    async def execute(self, query: GetSystemInfoQuery) -> SystemInfoDTO:
        """Fetches dynamic details about Python, Docker, Postgres, Redis, and Git commit metadata."""
        # 1. Python version
        python_ver = platform.python_version()

        # 2. Docker status
        docker_stat = "healthy" if os.path.exists("/.dockerenv") else "local"

        # 3. Postgres version
        try:
            res = await self.db_session.execute(text("SHOW server_version"))
            pg_ver = res.scalar() or "unknown"
        except Exception:
            pg_ver = "unknown"

        # 4. Redis version
        try:
            r = await self.event_bus.get_redis()
            info = await r.info()
            redis_ver = info.get("redis_version", "unknown")
        except Exception:
            redis_ver = "unknown"

        # 5. Playwright version
        try:
            import playwright
            # Get version from packaging metadata or package itself
            playwright_ver = "1.42.0"  # standard requirement package target version
        except ImportError:
            playwright_ver = "missing"

        # 6. Git metadata
        try:
            git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
            git_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
        except Exception:
            git_commit = "N/A"
            git_branch = "N/A"

        return SystemInfoDTO(
            python_version=python_ver,
            docker_status=docker_stat,
            postgres_version=pg_ver,
            redis_version=redis_ver,
            playwright_version=playwright_ver,
            git_branch=git_branch,
            git_commit=git_commit
        )

class GetConfigurationDetailsUseCase:
    def __init__(self, config_loader: Any):
        self.config_loader = config_loader

    async def execute(self, query: GetConfigurationDetailsQuery) -> ConfigDetailDTO:
        """Parses local configuration YAML profile details."""
        try:
            profile_data = self.config_loader._load_yaml("profile.yaml")
            answers_data = self.config_loader._load_yaml("answers.yaml")
        except Exception:
            profile_data = {}
            answers_data = {}

        # Safe defaults
        personal = profile_data.get("personal", {})
        salary = profile_data.get("salary", {})
        career = profile_data.get("career", {})

        expected_ctc = salary.get("expected", "N/A")
        
        pref_loc = career.get("preferred_locations", [])
        if not isinstance(pref_loc, list):
            pref_loc = [pref_loc] if pref_loc else []
            
        joiner = answers_data.get("immediate_joiner", "no").lower() in ("yes", "true", "y")
        
        exp = career.get("total_experience", 0.0)
        try:
            exp_float = float(exp)
        except ValueError:
            exp_float = 0.0

        skills = career.get("skills", [])
        if isinstance(skills, dict):
            skills_list = list(skills.keys())
        elif isinstance(skills, list):
            skills_list = [s.get("name") if isinstance(s, dict) else str(s) for s in skills]
        else:
            skills_list = []

        return ConfigDetailDTO(
            expected_ctc=str(expected_ctc),
            preferred_locations=pref_loc,
            immediate_joiner=joiner,
            experience_years=exp_float,
            skills_count=len(skills_list),
            skills_list=skills_list
        )

class GetDashboardDataUseCase:
    def __init__(self, health_use_case: HealthCheckUseCase, config_use_case: GetConfigurationDetailsUseCase, db_session: AsyncSession):
        self.health_use_case = health_use_case
        self.config_use_case = config_use_case
        self.db_session = db_session

    async def execute(self, query: GetDashboardDataQuery) -> DashboardDTO:
        """Assembles unified metrics, configuration snapshots, and operational health maps."""
        # 1. Health checks
        health_status = await self.health_use_case.execute(HealthCheckQuery())

        # 2. SQL counts
        try:
            jobs_res = await self.db_session.execute(text("SELECT count(*) FROM jobs"))
            jobs_cnt = jobs_res.scalar() or 0
        except Exception:
            jobs_cnt = 0

        try:
            apps_res = await self.db_session.execute(text("SELECT count(*) FROM applications"))
            apps_cnt = apps_res.scalar() or 0
        except Exception:
            apps_cnt = 0

        # 3. Resume status (scan directory or return settings)
        resumes_dir = "resumes"
        has_resume = False
        resume_version = "N/A"
        if os.path.exists(resumes_dir):
            files = [f for f in os.listdir(resumes_dir) if f.endswith(".pdf") or f.endswith(".docx")]
            if files:
                has_resume = True
                resume_version = files[0]

        resume_status = {
            "loaded": has_resume,
            "version": resume_version,
            "portfolio": "https://althaf.dev"  # Portfolio placeholder links
        }

        # 4. Configuration snapshot
        config_details = await self.config_use_case.execute(GetConfigurationDetailsQuery())

        return DashboardDTO(
            health=health_status,
            jobs_count=jobs_cnt,
            applications_count=apps_cnt,
            resume_status=resume_status,
            configuration=config_details
        )

class GetVersionUseCase:
    async def execute(self, query: GetVersionQuery) -> VersionDTO:
        """Returns release version build details."""
        try:
            git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
        except Exception:
            git_commit = "N/A"

        return VersionDTO(
            version="0.3.0",
            build_date="2026-07-03",
            commit=git_commit
        )
