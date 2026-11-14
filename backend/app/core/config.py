import os
from pathlib import Path
from pydantic_settings import BaseSettings

_this_file = Path(__file__).resolve()
# Look for policy_impact.db in project root or current working directory
_candidate_paths = [
    _this_file.parents[2] / "policy_impact.db",
    Path.cwd() / "policy_impact.db",
]
_resolved_db_path = None
for p in _candidate_paths:
    if p.is_file():
        _resolved_db_path = str(p).replace("\\", "/")
        break

if not _resolved_db_path:
    _resolved_db_path = str((_this_file.parents[2] / "policy_impact.db")).replace("\\", "/")

_default_db_url = f"sqlite:///{_resolved_db_path}"

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", _default_db_url)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_SET_JWT_SECRET_IN_ENV")

settings = Settings()

