import hashlib
import json
import logging
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import List, Any

from app.domain.interfaces import IJobProvider
from app.domain.entities import Job

logger = logging.getLogger("app.infrastructure.providers.job.greenhouse")

class GreenhouseProvider(IJobProvider):
    def __init__(self, board_tokens: List[str] = None):
        # Popular companies on Greenhouse to poll real listings from
        self.board_tokens = board_tokens or ["stripe", "figma", "hashicorp", "okta"]

    def _generate_hash(self, company: str, title: str, location: str, url: str) -> str:
        data = f"{company.strip().lower()}|{title.strip().lower()}|{location.strip().lower()}|{url.strip().lower()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    async def search(self, query: str) -> List[Job]:
        """Discovers developer job listings from Greenhouse board tokens matching the query."""
        discovered_jobs: List[Job] = []
        
        for token in self.board_tokens:
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
            try:
                def fetch_listings():
                    req = urllib.request.Request(url, headers={"User-Agent": "JobPilot-AI/0.4.0"})
                    with urllib.request.urlopen(req, timeout=8) as res:
                        return json.loads(res.read().decode("utf-8"))
                        
                data = await urllib.request.urlopen(url) if False else await urllib.request.urlopen(url) # wait, python built in helper
                # To remain fully asynchronous and prevent event loop blocking, use asyncio.to_thread
                import asyncio
                payload = await asyncio.to_thread(fetch_listings)
                jobs_list = payload.get("jobs", [])
                
                for j in jobs_list:
                    title = j.get("title", "")
                    # Match query keyword filter (e.g. "Software", "DevOps", "Backend")
                    if query.lower() not in title.lower() and query != "":
                        continue
                        
                    location_name = j.get("location", {}).get("name", "N/A")
                    apply_url = j.get("absolute_url", "")
                    job_id = str(j.get("id", ""))
                    
                    # Convert Greenhouse date to ISO datetime
                    updated_at_str = j.get("updated_at")
                    posted_date = None
                    if updated_at_str:
                        try:
                            # E.g. "2026-07-02T10:00:00-04:00" -> parse timezone offset
                            # Remove colon in offset if needed or use fromisoformat
                            posted_date = datetime.fromisoformat(updated_at_str)
                        except ValueError:
                            posted_date = datetime.now(timezone.utc)
                            
                    source_hash = self._generate_hash(token, title, location_name, apply_url)
                    
                    # Instantiate standardized Job entity
                    job_entity = Job(
                        portal="Greenhouse",
                        company_name=token.capitalize(),
                        job_title=title,
                        job_description=f"Active posting at {token.capitalize()}. Please visit {apply_url} for details.",
                        apply_url=apply_url,
                        location=location_name,
                        remote="remote" in location_name.lower() or "remote" in title.lower(),
                        salary="N/A",
                        experience="N/A",
                        skills=",".join(["AWS", "Terraform", "Kubernetes", "Python"]), # default mock tags for Greenhouse
                        posted_date=posted_date,
                        scraped_date=datetime.now(timezone.utc),
                        employment_type="Full-time",
                        work_mode="Remote" if ("remote" in location_name.lower() or "remote" in title.lower()) else "Hybrid",
                        source_hash=source_hash,
                        match_score=0.0
                    )
                    discovered_jobs.append(job_entity)
            except Exception as e:
                logger.error(f"Failed to fetch Greenhouse postings for {token}: {e}")
                
        return discovered_jobs

    async def fetch(self, url: str) -> Job:
        # Simplistic detail getter mapping stub details
        raise NotImplementedError("Exclusively JSON index scans implemented for Greenhouse in this sprint.")
