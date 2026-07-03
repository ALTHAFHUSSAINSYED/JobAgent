import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, REGISTRY

# Define standard Prometheus metrics collectors
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total count of HTTP requests processed by FastAPI.",
    ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP requests latency duration in seconds.",
    ["method", "endpoint"]
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        # Simplify path mapping to group path parameters (e.g. /api/v1/jobs/1 -> /api/v1/jobs/{id})
        endpoint = request.url.path
        
        # Don't track metric queries or websocket pathways to avoid spamming logs/counters
        if endpoint in ("/metrics", "/api/v1/metrics") or "ws" in request.url.scheme:
            return await call_next(request)
            
        start_time = time.time()
        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()
            return response
        except Exception as e:
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status="500").inc()
            raise e from None
        finally:
            duration = time.time() - start_time
            HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
