import os
import sys
import subprocess
from datetime import datetime

# Add backend to path to fetch scheme names
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.core.database import SessionLocal
from app.models.models import Scheme

def run_spider(spider_name, args=None):
    """Run a scrapy spider using subprocess."""
    print(f"[{datetime.utcnow().isoformat()}] Starting spider: {spider_name}")
    cmd = ["scrapy", "crawl", spider_name]
    if args:
        for k, v in args.items():
            cmd.extend(["-a", f"{k}={v}"])
            
    # Need to run in the scraper directory
    scraper_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        # Depending on if scrapy is installed globally or in .venv
        result = subprocess.run(cmd, cwd=scraper_dir, check=False)
        print(f"[{datetime.utcnow().isoformat()}] Finished spider: {spider_name} with exit code {result.returncode}")
    except Exception as e:
        print(f"Error running spider {spider_name}: {e}")

def main():
    print("--- Starting Local Policy ETL Pipeline ---")
    
    # 1. Scrape new schemes from government portals
    print("Step 1: Scraping state portals for new schemes...")
    run_spider("mahadbt_spider")

    # 2. Get active schemes from the DB to track mentions
    db = SessionLocal()
    try:
        schemes = db.query(Scheme).all()
        scheme_names = [s.name for s in schemes]
    finally:
        db.close()
        
    if not scheme_names:
        print("No schemes found in the database. Exiting.")
        return

    print(f"Found {len(scheme_names)} schemes in database to track.")
    schemes_arg = ",".join(scheme_names)

    # 3. Scrape News Mentions
    print("Step 2: Scraping News Mentions...")
    run_spider("news_mention_spider", {"scheme_names": schemes_arg})

    # 4. Scrape Social Media Mentions (Reddit)
    print("Step 3: Scraping Reddit Mentions...")
    run_spider("reddit_spider", {"scheme_names": schemes_arg})

    print("--- ETL Pipeline Finished ---")

if __name__ == "__main__":
    main()
