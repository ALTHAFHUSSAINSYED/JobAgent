from app.core.config import settings

class OpenRouterVerifier:
    def verify(self) -> bool:
        """Verifies if OpenRouter API Key is set in configuration."""
        key = settings.OPENROUTER_API_KEY
        if not key or key == "your_openrouter_api_key_here" or key == "":
            return False
        return True
