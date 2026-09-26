"""
run_rss_pipeline.py
-------------------
CLI entry point to run the full RSS pipeline:
  1. Scrape RSS feeds → raw_records
  2. Clean/normalize → cleaned_records
  3. Bridge to Mention table

Usage:
    cd LOCAL-POLICY-IMPACT-ANALYZER
    python -m scraper.rss.run_rss_pipeline
"""

import os
import sys

# Ensure the main project's backend is importable (needed by mention_bridge)
_this_dir = os.path.dirname(os.path.abspath(__file__))
_backend_path = os.path.abspath(os.path.join(_this_dir, "..", "..", "..", "backend"))
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

# Also ensure the LOCAL-POLICY-IMPACT-ANALYZER root is importable
_repo_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)


def main():
    print("=" * 60)
    print("RSS PIPELINE — Full Run")
    print("=" * 60)

    # Step 1: Scrape
    print("\n--- Step 1/3: Scraping RSS feeds ---")
    from scraper.rss.rss_pipeline import run_rss_scrape
    new_count, skipped = run_rss_scrape()
    print(f"  Result: {new_count} new, {skipped} duplicates skipped")

    # Step 2: Clean
    print("\n--- Step 2/3: Running data integration/cleaning ---")
    from scraper.rss.integration import run_integration
    run_integration()

    # Step 3: Bridge
    print("\n--- Step 3/3: Bridging to Mention table ---")
    from scraper.rss.mention_bridge import bridge_to_mentions
    stats = bridge_to_mentions()
    print(f"  Result: {stats}")

    print("\n" + "=" * 60)
    print("RSS PIPELINE — Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
