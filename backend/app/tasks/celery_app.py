"""
backend/app/tasks/celery_app.py
--------------------------------
Celery application configuration and task definitions.
Configures Redis broker and scheduled periodic scraping tasks.
"""

import os
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

REDIS_URL = settings.REDIS_URL or os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "policy_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "periodic-rss-scrape": {
            "task": "app.tasks.celery_app.scheduled_rss_scrape",
            "schedule": crontab(minute="0", hour="*/6"),  # Run every 6 hours
        },
    },
)


@celery_app.task(name="app.tasks.celery_app.scheduled_rss_scrape")
def scheduled_rss_scrape():
    """
    Periodic task: runs the RSS scrape pipeline and bridges new mentions.
    """
    try:
        from scraper.rss.rss_pipeline import run_rss_scrape
        from scraper.rss.integration import run_integration
        from scraper.rss.mention_bridge import bridge_to_mentions

        print("[Celery Beat] Starting scheduled RSS pipeline scrape...")
        inserted, skipped = run_rss_scrape()
        print(f"[Celery Beat] RSS Scrape complete: {inserted} inserted, {skipped} skipped.")

        print("[Celery Beat] Running data integration...")
        run_integration()

        print("[Celery Beat] Bridging to mentions with sentiment...")
        bridge_stats = bridge_to_mentions()
        print(f"[Celery Beat] Bridge complete: {bridge_stats}")

        return {
            "status": "success",
            "rss_inserted": inserted,
            "rss_skipped": skipped,
            "bridge_stats": bridge_stats,
        }
    except Exception as e:
        print(f"[Celery Beat] Pipeline error: {e}")
        return {"status": "error", "error": str(e)}
