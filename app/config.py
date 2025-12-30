import os

DRY_RUN = os.getenv("DRY_RUN", "False").lower() == "true"
AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "audit.jsonl")


