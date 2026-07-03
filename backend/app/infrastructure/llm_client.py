import time
import urllib.request
import asyncio
from app.core.config import settings

class OpenRouterVerifier:
    def verify(self) -> bool:
        """Verifies if OpenRouter API Key is set in configuration."""
        key = settings.OPENROUTER_API_KEY
        if not key or key == "your_openrouter_api_key_here" or key == "":
            return False
        return True

    async def get_latency(self) -> float:
        """Measures API connectivity latency to OpenRouter (in ms)."""
        start_time = time.time()
        try:
            url = "https://openrouter.ai/api/v1/models"
            def ping():
                req = urllib.request.Request(url, method="HEAD")
                # Exclude proxy configurations, directly connect
                with urllib.request.urlopen(req, timeout=4) as response:
                    return response.status == 200
            
            success = await asyncio.to_thread(ping)
            if success:
                return round((time.time() - start_time) * 1000, 2)
            return -1.0
        except Exception:
            return -1.0
