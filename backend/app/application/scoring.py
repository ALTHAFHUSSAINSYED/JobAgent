"""
Rule-Based Candidate Match Scoring Engine.

Scores a job based on how well it matches the candidate's known skills and preferences.
No AI or LLM usage in this sprint — pure keyword heuristics.
"""
from typing import Optional


# Keyword weight table — extend here as needed
KEYWORD_WEIGHTS: dict[str, int] = {
    "aws": 10,
    "amazon web services": 10,
    "terraform": 10,
    "kubernetes": 10,
    "k8s": 10,
    "docker": 5,
    "python": 5,
    "linux": 5,
    "hyderabad": 5,
    "remote": 5,
    "ansible": 5,
    "ci/cd": 5,
    "github actions": 5,
    "prometheus": 5,
    "grafana": 5,
    "postgresql": 5,
    "fastapi": 5,
    "react": 5,
    "devops": 5,
    "platform engineering": 5,
    "cloud": 3,
    "microservices": 3,
    "rest api": 3,
    "api": 2,
}

MAX_SCORE = 100


def calculate_match_score(
    job_title: str,
    job_description: str,
    skills: Optional[str],
    location: Optional[str],
    work_mode: Optional[str],
) -> float:
    """
    Calculates a candidate match score for a job listing (0.0 to 100.0).
    Matches keywords in title, description, skills, location, and work_mode.
    """
    # Combine all job text into a single lowercased blob
    text_blob = " ".join(filter(None, [
        job_title or "",
        job_description or "",
        skills or "",
        location or "",
        work_mode or "",
    ])).lower()

    score = 0
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword.lower() in text_blob:
            score += weight

    # Cap score at MAX_SCORE
    return min(float(score), float(MAX_SCORE))
