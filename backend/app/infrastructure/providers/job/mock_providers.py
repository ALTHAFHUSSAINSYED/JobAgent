import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Any
from app.domain.interfaces import IJobProvider
from app.domain.entities import Job

class MockJobProvider(IJobProvider):
    def __init__(self, portal_name: str):
        self.portal_name = portal_name

    def _generate_hash(self, company: str, title: str, location: str, url: str) -> str:
        data = f"{company.strip().lower()}|{title.strip().lower()}|{location.strip().lower()}|{url.strip().lower()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    async def search(self, query: str) -> List[Job]:
        """Returns mock postings structured with varying keyword weights for dashboard scoring checks."""
        mock_jobs = [
            # Job 1: High matching score (AWS, Terraform, Kubernetes, Linux, Remote) -> Expected Score 45
            {
                "company": "CloudTech Solutions",
                "title": "Senior DevOps Engineer (AWS & Terraform)",
                "location": "Hyderabad, India",
                "remote": True,
                "skills": "AWS,Terraform,Kubernetes,Linux",
                "work_mode": "Remote",
                "salary": "18 - 25 LPA",
                "experience": "5+ Years",
                "description": "We are seeking a Senior DevOps expert with strong hands-on AWS, Terraform, and Kubernetes deployments experience in production cloud systems."
            },
            # Job 2: Mid matching score (Python, Docker, Linux) -> Expected Score 15
            {
                "company": "Alpha Software Labs",
                "title": "Backend Python Developer",
                "location": "Bengaluru, India",
                "remote": False,
                "skills": "Python,Docker,Linux",
                "work_mode": "On-site",
                "salary": "12 - 16 LPA",
                "experience": "3+ Years",
                "description": "Alpha Labs is looking for a python developer to build microservices containers using Docker. Linux experience is an added advantage."
            },
            # Job 3: Low matching score (only Hyderabad, Remote) -> Expected Score 10
            {
                "company": "Global Systems Inc",
                "title": "System Analyst",
                "location": "Hyderabad, India",
                "remote": True,
                "skills": "Java,Spring Boot,MySQL",
                "work_mode": "Remote",
                "salary": "8 - 10 LPA",
                "experience": "2+ Years",
                "description": "Maintain enterprise Java databases and generate systems mapping analytics documents."
            }
        ]

        jobs_list: List[Job] = []
        for idx, mj in enumerate(mock_jobs):
            # Check filter query
            if query.lower() not in mj["title"].lower() and query != "":
                continue
                
            apply_url = f"https://jobs.{self.portal_name.lower()}.com/posting/{idx + 101}"
            source_hash = self._generate_hash(mj["company"], mj["title"], mj["location"], apply_url)
            
            job_entity = Job(
                portal=self.portal_name,
                company_name=mj["company"],
                job_title=mj["title"],
                job_description=mj["description"],
                apply_url=apply_url,
                location=mj["location"],
                remote=mj["remote"],
                salary=mj["salary"],
                experience=mj["experience"],
                skills=mj["skills"],
                posted_date=datetime.now(timezone.utc) - timedelta(days=idx),
                scraped_date=datetime.now(timezone.utc),
                employment_type="Full-time",
                work_mode=mj["work_mode"],
                source_hash=source_hash,
                match_score=0.0
            )
            jobs_list.append(job_entity)
            
        return jobs_list

    async def fetch(self, url: str) -> Job:
        raise NotImplementedError("Exclusively mock listings scans supported.")
