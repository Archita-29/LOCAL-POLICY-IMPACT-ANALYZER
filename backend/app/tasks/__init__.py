"""
Celery background tasks package for Local Policy Impact Analyzer.
"""
from app.tasks.celery_app import celery_app

__all__ = ["celery_app"]
