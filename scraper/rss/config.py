"""
scraper/rss/config.py
---------------------
Shared configuration and database URL resolution for the RSS scraper package.
Ensures modules connect to the proper database regardless of working directory.
"""

import os


def get_database_url() -> str:
    """
    Resolve the SQLAlchemy database connection URL:
      1. Use DATABASE_URL environment variable if set.
      2. If the parent project's backend/policy_impact.db exists, use it.
      3. Otherwise fall back to local sqlite:///policy_impact.db.
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    this_dir = os.path.dirname(os.path.abspath(__file__))
    local_backend_db = os.path.abspath(
        os.path.join(this_dir, "..", "..", "backend", "policy_impact.db")
    )
    if os.path.exists(local_backend_db):
        clean_path = local_backend_db.replace("\\", "/")
        return f"sqlite:///{clean_path}"

    parent_backend_db = os.path.abspath(
        os.path.join(this_dir, "..", "..", "..", "backend", "policy_impact.db")
    )
    if os.path.exists(parent_backend_db):
        clean_path = parent_backend_db.replace("\\", "/")
        return f"sqlite:///{clean_path}"

    return "sqlite:///policy_impact.db"
