import logging
import os
import platform
import subprocess
import sys
import time
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
from app.infrastructure.database import async_engine
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
        details = self.playwright_verifier.get_details()
        playwright_ver = details.get("version", "N/A")

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

        expected_ctc = "N/A"
        pref_loc = []
        joiner = False
        exp_float = 0.0
        skills_list = []

        try:
            # Safe defaults
            personal = profile_data.get("personal", {})
            salary = profile_data.get("salary", {})
            career = profile_data.get("career", {})

            for key in ["expected", "expected_ctc_lpa", "expected_ctc"]:
                if salary.get(key) is not None:
                    expected_ctc = str(salary.get(key))
                    break
            
            pref_loc = career.get("preferred_locations") or career.get("locations") or []
            if not isinstance(pref_loc, list):
                pref_loc = [pref_loc] if pref_loc else []
                
            val = answers_data.get("immediate_joiner")
            if val is not None:
                if isinstance(val, str):
                    joiner = val.lower() in ("yes", "true", "y")
                else:
                    joiner = bool(val)
            
            exp = career.get("total_experience")
            if exp is None:
                exp = career.get("experience")
                
            from app.infrastructure.config.yaml_loader import parse_experience_years
            exp_float = parse_experience_years(exp)

            skills = career.get("skills", [])
            if isinstance(skills, dict):
                skills_list = list(skills.keys())
            elif isinstance(skills, list):
                skills_list = [s.get("name") if isinstance(s, dict) else str(s) for s in skills]
        except Exception as e:
            logger.warning(f"Error parsing configuration details, using safe defaults: {e}")

        return ConfigDetailDTO(
            expected_ctc=expected_ctc,
            preferred_locations=pref_loc,
            immediate_joiner=joiner,
            experience_years=exp_float,
            skills_count=len(skills_list),
            skills_list=skills_list
        )

class GetDashboardDataUseCase:
    def __init__(self, health_use_case: HealthCheckUseCase, config_use_case: GetConfigurationDetailsUseCase, db_session: AsyncSession, resume_manager: Any):
        self.health_use_case = health_use_case
        self.config_use_case = config_use_case
        self.db_session = db_session
        self.resume_manager = resume_manager

    async def execute(self, query: GetDashboardDataQuery) -> DashboardDTO:
        """Assembles unified metrics, configuration snapshots, and operational health maps with latencies."""
        # 1. Run Health Checks
        health_status = await self.health_use_case.execute(HealthCheckQuery())

        # 2. Database latency & connection pool details
        db_start = time.time()
        try:
            await self.db_session.execute(text("SELECT 1"))
            db_ms = round((time.time() - db_start) * 1000, 2)
        except Exception:
            db_ms = -1.0

        # Connection Pool statistics
        pool = async_engine.pool
        pool_details = {
            "active": pool.checkedout(),
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "max": pool.size() + getattr(pool, "_max_overflow", 10)
        }

        # 3. Redis connection latency
        redis_start = time.time()
        try:
            await self.health_use_case.event_bus.publish("health.ping", {"ping": "pong"})
            redis_ms = round((time.time() - redis_start) * 1000, 2)
        except Exception:
            redis_ms = -1.0

        # 4. OpenRouter verification & connectivity latency
        openrouter_ms = await self.health_use_case.settings_verifier.get_latency()

        # Compile latency mappings
        latencies = {
            "database_ms": db_ms,
            "redis_ms": redis_ms,
            "openrouter_ms": openrouter_ms
        }

        # 5. SQL database counts
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

        # 6. Scan resumes folder
        resumes = self.resume_manager.scan_resumes()
        
        # Check active resume attachments
        master_resume = "N/A"
        ats_resume = "N/A"
        has_resume = False
        
        for res in resumes:
            has_resume = True
            if res.get("type") == "Portfolio Resume":
                master_resume = res.get("filename")
            elif res.get("type") == "ATS Resume":
                ats_resume = res.get("filename")

        resume_status = {
            "loaded": has_resume,
            "master": master_resume,
            "ats": ats_resume,
            "portfolio": "https://althafportfolio.site/"
        }

        # 7. Local configuration details
        config_details = await self.config_use_case.execute(GetConfigurationDetailsQuery())
        
        # Playwright executable details
        playwright_details = self.health_use_case.playwright_verifier.get_details()

        return DashboardDTO(
            health=health_status,
            jobs_count=jobs_cnt,
            applications_count=apps_cnt,
            resume_status=resume_status,
            configuration=config_details,
            latencies=latencies,
            database_pool=pool_details,
            resumes=resumes,
            playwright_details=playwright_details
        )

class GetVersionUseCase:
    async def execute(self, query: GetVersionQuery) -> VersionDTO:
        """Returns release version build details."""
        try:
            git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
        except Exception:
            git_commit = "N/A"

        return VersionDTO(
            version="0.5.0",  # Bumped version for Sprint 1.5 CI/CD + Sprint 2.1 Job Discovery
            build_date="2026-07-03",
            commit=git_commit
        )


class DiscoverJobsUseCase:
    """
    Runs all active job providers, de-duplicates listings via SHA-256 hashes,
    computes match scores, and persists new jobs into PostgreSQL.
    """
    def __init__(self, session: AsyncSession, event_bus: IEventBus):
        from app.infrastructure.repositories.job import SQLAlchemyJobRepository
        from app.infrastructure.providers.job.greenhouse import GreenhouseProvider
        from app.infrastructure.providers.job.lever import LeverProvider
        from app.infrastructure.providers.job.mock_providers import MockJobProvider
        from app.application.scoring import calculate_match_score
        from app.infrastructure.database.models import JobModel as JM
        import uuid

        self.session = session
        self.event_bus = event_bus
        self.job_repo = SQLAlchemyJobRepository(session)
        self.providers = [
            GreenhouseProvider(),
            LeverProvider(),
            MockJobProvider("LinkedIn"),
            MockJobProvider("Naukri"),
            MockJobProvider("Foundit"),
        ]
        self._calculate_score = calculate_match_score
        self._uuid = uuid

    async def execute(self, query_term: str = "") -> Dict[str, Any]:
        from app.infrastructure.database.models import JobModel as JM
        import uuid
        from datetime import datetime, timezone

        new_count = 0
        skipped_count = 0
        total_errors = 0

        for provider in self.providers:
            try:
                jobs = await provider.search(query_term)
                for job in jobs:
                    # Duplicate detection
                    exists = await self.job_repo.exists_by_hash(job.source_hash)
                    if exists:
                        skipped_count += 1
                        continue

                    # Calculate candidate match score
                    score = self._calculate_score(
                        job_title=job.job_title,
                        job_description=job.job_description,
                        skills=job.skills,
                        location=job.location,
                        work_mode=job.work_mode,
                    )

                    # Persist job to database
                    job_model = JM(
                        id=job.id,
                        portal=job.portal,
                        company_name=job.company_name,
                        job_title=job.job_title,
                        job_description=job.job_description,
                        apply_url=job.apply_url,
                        location=job.location,
                        remote=job.remote,
                        salary=job.salary,
                        experience=job.experience,
                        skills=job.skills,
                        posted_date=job.posted_date,
                        scraped_date=job.scraped_date,
                        employment_type=job.employment_type,
                        work_mode=job.work_mode,
                        source_hash=job.source_hash,
                        match_score=score,
                        status="discovered",
                        created_at=datetime.now(timezone.utc),
                    )
                    self.session.add(job_model)
                    new_count += 1

                await self.session.commit()
            except Exception as e:
                logger.error(f"Job discovery error for provider {provider.__class__.__name__}: {e}")
                await self.session.rollback()
                total_errors += 1

        # Broadcast event
        try:
            await self.event_bus.publish("jobs.updated", {
                "new": new_count,
                "skipped": skipped_count,
                "errors": total_errors
            })
        except Exception:
            pass

        logger.info(f"Job discovery complete: {new_count} new, {skipped_count} skipped, {total_errors} errors")
        return {"new": new_count, "skipped": skipped_count, "errors": total_errors}


class GetJobsUseCase:
    """Lists jobs from PostgreSQL with filtering, sorting, and pagination."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(
        self,
        search: str = "",
        portal: str = "",
        work_mode: str = "",
        sort_by: str = "match_score",
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        from sqlalchemy import select, func
        from app.infrastructure.database.models import JobModel as JM

        stmt = select(JM)

        # Apply filters
        if search:
            stmt = stmt.where(
                JM.job_title.ilike(f"%{search}%") |
                JM.company_name.ilike(f"%{search}%") |
                JM.job_description.ilike(f"%{search}%")
            )
        if portal:
            stmt = stmt.where(JM.portal.ilike(f"%{portal}%"))
        if work_mode:
            stmt = stmt.where(JM.work_mode.ilike(f"%{work_mode}%"))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        # Apply sorting
        if sort_by == "posted_date":
            stmt = stmt.order_by(JM.posted_date.desc().nullsfirst())
        elif sort_by == "created_at":
            stmt = stmt.order_by(JM.created_at.desc())
        else:
            stmt = stmt.order_by(JM.match_score.desc().nullsfirst())

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        rows = (await self.session.execute(stmt)).scalars().all()

        def _serialise(m: JM) -> Dict[str, Any]:
            return {
                "id": str(m.id),
                "portal": m.portal,
                "company": m.company_name,
                "title": m.job_title,
                "location": m.location,
                "remote": m.remote,
                "salary": m.salary,
                "experience": m.experience,
                "skills": m.skills,
                "apply_url": m.apply_url,
                "posted_date": m.posted_date.isoformat() if m.posted_date else None,
                "scraped_date": m.scraped_date.isoformat() if m.scraped_date else None,
                "employment_type": m.employment_type,
                "work_mode": m.work_mode,
                "match_score": float(m.match_score) if m.match_score is not None else 0.0,
                "status": m.status,
                "description": m.job_description,
            }

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": max(1, (total + page_size - 1) // page_size),
            "jobs": [_serialise(r) for r in rows],
        }
