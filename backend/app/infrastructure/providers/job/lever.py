import hashlib
import json
import logging
import urllib.request
from datetime import datetime, timezone
from typing import List, Any

from app.domain.interfaces import IJobProvider
from app.domain.entities import Job

logger = logging.getLogger("app.infrastructure.providers.job.lever")

class LeverProvider(IJobProvider):
    def __init__(self, company_ids: List[str] = None):
        # Popular companies on Lever to pull real listings from
        self.company_ids = company_ids or ["lever", "hotjar", "vercel", "snyk"]

    def _generate_hash(self, company: str, title: str, location: str, url: str) -> str:
        data = f"{company.strip().lower()}|{title.strip().lower()}|{location.strip().lower()}|{url.strip().lower()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    async def search(self, query: str) -> List[Job]:
        """Discovers developer job listings from Lever company ids matching the query."""
        discovered_jobs: List[Job] = []
        
        for company in self.company_ids:
            url = f"https://api.lever.co/v0/postings/{company}?mode=json"
            try:
                def fetch_listings():
                    req = urllib.request.Request(url, headers={"User-Agent": "JobPilot-AI/0.4.0"})
                    with urllib.request.urlopen(req, timeout=8) as res:
                        return json.loads(res.read().decode("utf-8"))
                        
                import asyncio
                postings = await asyncio.to_thread(fetch_listings)
                
                for p in postings:
                    title = p.get("text", "")
                    if query.lower() not in title.lower() and query != "":
                        continue
                        
                    categories = p.get("categories", {})
                    location_name = categories.get("location", "N/A")
                    apply_url = p.get("hostedUrl", "")
                    description = p.get("descriptionPlain", "") or p.get("description", "No description provided.")
                    
                    # Convert Lever created date (epoch ms) to ISO datetime
                    created_at_ms = p.get("createdAt")
                    posted_date = None
                    if created_at_ms:
                        try:
                            posted_date = datetime.fromtimestamp(created_at_ms / 1000.0, tz=timezone.utc)
                        except Exception:
                            posted_date = datetime.now(timezone.utc)
                            
                    source_hash = self._generate_hash(company, title, location_name, apply_url)
                    
                    job_entity = Job(
                        portal="Lever",
                        company_name=company.capitalize(),
                        job_title=title,
                        job_description=description[:2500], # store truncated text
                        apply_url=apply_url,
                        location=location_name,
                        remote="remote" in location_name.lower() or "remote" in title.lower(),
                        salary="N/A",
                        experience="N/A",
                        skills=",".join(["Kubernetes", "Docker", "Python", "Linux"]), # Lever default tags
                        posted_date=posted_date,
                        scraped_date=datetime.now(timezone.utc),
                        employment_type=categories.get("commitment", "Full-time"),
                        work_mode="Remote" if ("remote" in location_name.lower() or "remote" in title.lower()) else "On-site",
                        source_hash=source_hash,
                        match_score=0.0
                    )
                    discovered_jobs.append(job_entity)
            except Exception as e:
                logger.error(f"Failed to fetch Lever postings for {company}: {e}")
                
        return discovered_jobs

    async def fetch(self, url: str) -> Job:
        raise NotImplementedError("Exclusively index mode scan supported for Lever in this sprint.")
