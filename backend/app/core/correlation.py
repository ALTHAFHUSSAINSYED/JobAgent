from contextvars import ContextVar

# Thread-safe/async context variable for correlation ID
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")
