class DomainException(Exception):
    """Base exception for all domain errors."""
    pass

class ConfigurationError(DomainException):
    """Raised when config parameters are invalid or missing."""
    pass

class EntityNotFoundError(DomainException):
    """Raised when a queried entity does not exist."""
    pass

class DatabaseConnectionError(DomainException):
    """Raised when connection to database fails."""
    pass

class CacheConnectionError(DomainException):
    """Raised when connection to cache/event broker fails."""
    pass
