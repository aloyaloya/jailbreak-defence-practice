import json
import hashlib
from datetime import datetime
from app.config import AUDIT_LOG_PATH

class AuditLogger:
    def __init__(self):
        self.log_path = AUDIT_LOG_PATH
    
    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    def log(self, text: str, verdict: str, layer: str = None, confidence: float = None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "text_hash": self._hash_text(text),
            "verdict": verdict,
            "layer": layer,
            "ai_confidence": confidence
        }
        
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


