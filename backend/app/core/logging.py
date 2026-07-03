import logging
import logging.config
import os

class CorrelationFilter(logging.Filter):
    """Logging filter to inject correlation ID context into formatting."""
    def filter(self, record):
        from app.core.correlation import correlation_id_ctx
        record.correlation_id = correlation_id_ctx.get() or "N/A"
        return True

def setup_logging():
    # Make sure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] [%(levelname)s] [CorrID: %(correlation_id)s] [%(name)s:%(lineno)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
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
                "formatter": "standard",
                "filters": ["correlation_filter"],
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filters": ["correlation_filter"],
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": True
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
