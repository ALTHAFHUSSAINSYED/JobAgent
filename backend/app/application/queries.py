from pydantic import BaseModel

class HealthCheckQuery(BaseModel):
    """Query to trigger health checks on system dependencies."""
    pass

class GetSystemInfoQuery(BaseModel):
    """Query to retrieve system dependencies and versions metadata."""
    pass

class GetConfigurationDetailsQuery(BaseModel):
    """Query to retrieve structured parameters from profile configuration files."""
    pass

class GetDashboardDataQuery(BaseModel):
    """Query to retrieve high level counts and diagnostics for dashboard."""
    pass

class GetVersionQuery(BaseModel):
    """Query to retrieve release version details."""
    pass
