import logging

logger = logging.getLogger("app.infrastructure.browser_client")

class PlaywrightVerifier:
    def verify(self) -> bool:
        """Verifies Playwright package installation presence."""
        try:
            import playwright
            return True
        except ImportError:
            logger.warning("Playwright package is not installed.")
            return False
