import os
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

    def get_details(self) -> dict:
        """Exposes local Playwright Chromium executable paths and version metrics."""
        installed = self.verify()
        if not installed:
            return {
                "installed": False,
                "version": "N/A",
                "executable_path": "N/A",
                "ready": False
            }
            
        # Search for chromium binaries in standard cache paths
        cache_paths = [
            os.path.expanduser("~/.cache/ms-playwright"),
            "/root/.cache/ms-playwright"
        ]
        
        exec_path = "N/A"
        version = "unknown"
        ready = False
        
        for cache_dir in cache_paths:
            if os.path.exists(cache_dir):
                try:
                    for entry in os.scandir(cache_dir):
                        if entry.is_dir() and "chromium" in entry.name:
                            # Linux path structure
                            test_path = os.path.join(entry.path, "chrome-linux", "chrome")
                            if not os.path.exists(test_path):
                                # Windows path structure
                                test_path = os.path.join(entry.path, "chrome-win", "chrome.exe")
                            
                            if os.path.exists(test_path):
                                exec_path = test_path
                                version = entry.name.split("-")[-1] if "-" in entry.name else entry.name
                                ready = True
                                break
                except Exception as e:
                    logger.error(f"Error scanning browser cache paths: {e}")
                    
        # If playwright is present, but chrome binary not matched yet, mark library ready
        if not ready and installed:
            ready = True
            
        return {
            "installed": True,
            "version": f"Chromium {version}",
            "executable_path": exec_path,
            "ready": ready
        }
