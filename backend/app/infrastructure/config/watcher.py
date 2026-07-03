import asyncio
import os
import logging
from typing import Callable, Dict

logger = logging.getLogger("app.infrastructure.config.watcher")

class ConfigWatcher:
    def __init__(self, config_dir: str = "config", interval_seconds: float = 2.0):
        self.config_dir = config_dir
        self.interval_seconds = interval_seconds
        self.file_mtimes: Dict[str, float] = {}
        self.is_running = False
        self.watch_files = ["profile.yaml", "answers.yaml", "companies.yaml"]

    def _get_mtime(self, filename: str) -> float:
        path = os.path.join(self.config_dir, filename)
        if os.path.exists(path):
            return os.path.getmtime(path)
        return 0.0

    def init_states(self) -> None:
        """Pre-populate initial file modification times."""
        for filename in self.watch_files:
            self.file_mtimes[filename] = self._get_mtime(filename)

    async def start(self, on_change_callback: Callable[[str], asyncio.Task]) -> None:
        """Starts background file monitoring loop."""
        self.init_states()
        self.is_running = True
        logger.info("Configuration hot-reload file watcher active.")
        
        while self.is_running:
            try:
                await asyncio.sleep(self.interval_seconds)
                for filename in self.watch_files:
                    current_mtime = self._get_mtime(filename)
                    previous_mtime = self.file_mtimes.get(filename, 0.0)
                    
                    if current_mtime != previous_mtime:
                        self.file_mtimes[filename] = current_mtime
                        logger.info(f"Detected modification in configuration file: {filename}")
                        
                        # Trigger reload check callback
                        if asyncio.iscoroutinefunction(on_change_callback):
                            await on_change_callback(filename)
                        else:
                            on_change_callback(filename)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in config watcher loop: {e}")

    def stop(self) -> None:
        self.is_running = False
