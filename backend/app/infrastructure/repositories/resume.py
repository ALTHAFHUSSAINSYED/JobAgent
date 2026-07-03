import os
import hashlib
import logging
from typing import Dict, Any, List

logger = logging.getLogger("app.infrastructure.repositories.resume")

class ResumeManager:
    def __init__(self, resumes_dir: str = "resumes"):
        self.resumes_dir = resumes_dir

    def calculate_sha256(self, filepath: str) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {filepath}: {e}")
            return "unknown"

    def scan_resumes(self) -> List[Dict[str, Any]]:
        """Scans resumes folder, returns size, modification timestamps, and content hashes."""
        if not os.path.exists(self.resumes_dir):
            os.makedirs(self.resumes_dir, exist_ok=True)
            
        resumes = []
        try:
            for entry in os.scandir(self.resumes_dir):
                if entry.is_file() and entry.name.lower().endswith((".pdf", ".docx")):
                    filepath = entry.path
                    stats = entry.stat()
                    file_hash = self.calculate_sha256(filepath)
                    
                    # Classify resume type
                    res_type = "ATS Resume"
                    if "portfolio" in entry.name.lower() or "master" in entry.name.lower():
                        res_type = "Portfolio Resume"
                        
                    resumes.append({
                        "filename": entry.name,
                        "size_bytes": stats.st_size,
                        "last_modified": stats.st_mtime,
                        "sha256": file_hash,
                        "type": res_type
                    })
        except Exception as e:
            logger.error(f"Error scanning resumes folder: {e}")
            
        return resumes
