from pydantic import BaseModel

class HealthCheckQuery(BaseModel):
    """Query to trigger health checks on system dependencies."""
    pass
