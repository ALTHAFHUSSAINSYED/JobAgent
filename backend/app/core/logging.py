import collections
import json
import logging
import logging.config
import os
import asyncio

# In-memory history for GET /logs
log_history = collections.deque(maxlen=100)

# List of active asyncio queues for WebSocket streaming
active_connections = []

class CorrelationFilter(logging.Filter):
    """Logging filter to inject correlation ID context into formatting."""
    def filter(self, record):
        from app.core.correlation import correlation_id_ctx
        record.correlation_id = correlation_id_ctx.get() or "N/A"
        return True

class JSONFormatter(logging.Formatter):
    """Formats logs into structured JSON strings."""
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "correlation_id": getattr(record, "correlation_id", "N/A"),
            "module": record.name,
            "line": record.lineno,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

class InMemoryLogHandler(logging.Handler):
    """Intercepts and stores logs in memory, distributing to active WebSocket queues."""
    def emit(self, record):
        try:
            formatted = self.format(record)
            log_history.append(formatted)
            
            # Broadcast to active socket loops
            for queue in active_connections:
                try:
                    queue.put_nowait(formatted)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "app.core.logging.JSONFormatter"
            }
        },
        "filters": {
            "correlation_filter": {
                "()": "app.core.logging.CorrelationFilter"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "filters": ["correlation_filter"],
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filters": ["correlation_filter"],
                "filename": "logs/app.json.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "memory": {
                "class": "app.core.logging.InMemoryLogHandler",
                "formatter": "json",
                "filters": ["correlation_filter"]
            }
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file", "memory"],
                "level": "INFO",
                "propagate": True
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
