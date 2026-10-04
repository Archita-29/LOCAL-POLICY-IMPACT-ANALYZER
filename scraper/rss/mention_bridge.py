"""
mention_bridge.py
-----------------
Bridge module: reads cleaned RSS records and inserts matching ones
as Mention rows in the main backend's mentions table with sentiment analysis.

This connects Antra's RSS pipeline output to the main project's
impact scoring system.

HOW MATCHING WORKS:
  Bilingual pattern matching (Hindi, English, Hinglish) maps news headlines
  to specific schemes (e.g. "पीएम किसान" -> "PM Kisan Samman Nidhi").
  If sentiment analyzer is available, computes sentiment_score and sentiment_label.
"""

import os
import sys
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the main project's backend and ml to sys.path
_this_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
_parent_root = os.path.abspath(os.path.join(_repo_root, ".."))

for p in [
    os.path.join(_repo_root, "backend"),
    os.path.join(_repo_root, "ml"),
    _repo_root,
    os.path.join(_parent_root, "backend"),
    os.path.join(_parent_root, "ml"),
    _parent_root,
]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from scraper.rss.models import Base as RSSBase, CleanedRecord
from scraper.rss.config import get_database_url
from scraper.rss.sentiment import predict_sentiment
from app.core.database import Base as BackendBase
from app.models.models import Scheme, Mention, ImpactScore

DATABASE_URL = get_database_url()

# Bilingual pattern dictionary for mapping news to schemes
SCHEME_PATTERNS = {
    "PM Kisan Samman Nidhi": ["pm kisan", "pm-kisan", "kisan samman", "पीएम किसान", "किसान सम्मान", "₹6000", "6000 रुपये", "kisan helpline"],
    "Pradhan Mantri Awas Yojana – Urban 2.0 & Gramin": ["pm awas", "pmay", "awas yojana", "पीएम आवास", "आवास योजना", "मकान", "housing scheme"],
    "Ayushman Bharat - PMJAY": ["ayushman", "pmjay", "आयुष्मान", "7 लाख रुपये का बीमा", "स्वास्थ्य योजना", "मुफ्त इलाज"],
    "Atal Bhujal Yojana": ["atal bhujal", "अटल भूजल", "भूजल", "groundwater", "जल शक्ति", "सिंचाई"],
    "Atal Pension Yojana & PM Maandhan": ["atal pension", "अटल पेंशन", "मानधन", "maandhan", "5000 रुपये की पेंशन", "5000 रुपये पेंशन"],
    "Kisan Credit Card (KCC) Scheme": ["kcc", "किसान क्रेडिट कार्ड", "kisan credit", "कृषि यंत्रों पर 80% तक सब्सिडी", "ट्रैक्‍टर खरीदने"],
    "Mutual Credit Guarantee Scheme for MSMEs": ["mutual credit guarantee", "credit guarantee scheme", "msme", "क्रेडिट गारंटी"],
    "Weather-Based Crop Insurance Scheme (RWBCIS)": ["crop insurance", "weather- based crop", "weather-based", "फसल बीमा", "सोयाबीन की फ़सल", "apple crop"],
    "Mukhyamantri Majhi Ladki Bahin Yojana": ["majhi ladki", "लाडकी बहीण", "ladki bahin", "लाड़की बहिन", "ladki behan"],
    "Ladli Behna Yojana": ["ladli behna", "लाडली बहना", "लाड़ली बहना"],
    "Chief Minister's Breakfast Scheme": ["breakfast scheme", "free breakfast", "नाश्ता योजना", "breakfast for schoolkids", "stalin's breakfast"],
    "Mukhyamantri Mahila Rojgar & Vivah Yojana": ["mahila rojgar", "शादी आप करिए, पैसा सरकार देगी", "महिलाओं के खाते में ₹10,000", "रोजगार", "सेवा सेतु अभियान"],
    "MahaDBT Post-Matric Scholarship": ["mahadbt", "post-matric", "scholarship", "छात्रवृत्ति", "swadhar", "स्वाधार"],
    "Sanjay Gandhi Niradhar Anudan Yojana": ["sanjay gandhi", "niradhar", "निराधार", "वृद्धावस्था"],
}


def bridge_to_mentions(db_url: str | None = None) -> dict:
    """
    Read cleaned_records, resolve matching schemes via bilingual patterns,
    run NLP sentiment analysis, and insert Mentions into backend mentions table.
    """
    url = db_url or DATABASE_URL
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args)

    RSSBase.metadata.create_all(engine)
    BackendBase.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    stats = {"inserted": 0, "skipped_no_match": 0, "skipped_duplicate": 0}

    try:
        schemes = session.query(Scheme).all()
        if not schemes:
            print("WARNING: No schemes found in database.")
            return stats

        scheme_name_map = {s.name: s for s in schemes}

        # Pre-fetch existing mentions into sets for fast O(1) deduplication
        existing_urls = {
            (m.scheme_id, m.url.strip())
            for m in session.query(Mention.scheme_id, Mention.url).filter(Mention.url.isnot(None)).all()
            if m.url
        }
        existing_texts = {
            (m.scheme_id, (m.raw_text or "").strip().lower())
            for m in session.query(Mention.scheme_id, Mention.raw_text).all()
        }

        cleaned_rows = (
            session.query(CleanedRecord)
            .filter(CleanedRecord.is_policy_relevant == 1)
            .filter(CleanedRecord.is_near_duplicate == 0)
            .all()
        )
        print(f"Found {len(cleaned_rows)} cleaned records (relevant, non-duplicate).")

        for row in cleaned_rows:
            search_text = f"{row.title_clean or ''} {row.summary_clean or ''}".lower()

            matched_scheme = None
            # 1. Check bilingual alias patterns
            for scheme_name, patterns in SCHEME_PATTERNS.items():
                if any(p.lower() in search_text for p in patterns):
                    if scheme_name in scheme_name_map:
                        matched_scheme = scheme_name_map[scheme_name]
                        break

            # 2. Check direct substring on existing scheme names
            if not matched_scheme:
                for s in schemes:
                    if s.name.lower() in search_text:
                        matched_scheme = s
                        break

            if not matched_scheme:
                stats["skipped_no_match"] += 1
                continue

            # In-memory deduplication check (URL or exact text match for this scheme)
            row_link = (row.link or "").strip()
            row_title = (row.title_clean or "").strip()
            url_key = (matched_scheme.id, row_link) if row_link else None
            text_key = (matched_scheme.id, row_title.lower())

            if (url_key and url_key in existing_urls) or (text_key in existing_texts):
                stats["skipped_duplicate"] += 1
                continue

            # Determine sentiment
            sent_score = Decimal("0.0")
            sent_label = "Neutral"
            if predict_sentiment:
                nlp_res = predict_sentiment(f"{row.title_clean or ''} {row.summary_clean or ''}")
                sent_score = Decimal(str(nlp_res["sentiment_score"]))
                sent_label = nlp_res["sentiment_label"]

            lang_map = {"hindi": "hi", "english": "en", "hinglish": "hi-en"}
            mention_lang = lang_map.get(row.language, "hi")

            pub_dt = datetime.now(timezone.utc)
            if row.published_datetime:
                try:
                    pub_dt = datetime.fromisoformat(row.published_datetime.replace("Z", "+00:00"))
                except Exception:
                    pub_dt = datetime.now(timezone.utc)

            mention = Mention(
                scheme_id=matched_scheme.id,
                source=f"RSS: {row.source}" if row.source else "RSS",
                raw_text=row_title,
                language=mention_lang,
                sentiment_score=sent_score,
                sentiment_label=sent_label,
                published_date=pub_dt,
                url=row_link if row_link else None,
            )
            session.add(mention)
            if url_key:
                existing_urls.add(url_key)
            existing_texts.add(text_key)
            stats["inserted"] += 1

        session.commit()
        print(f"\nBridge complete: {stats}")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()

    return stats


if __name__ == "__main__":
    bridge_to_mentions()
