# LOCAL-POLICY-IMPACT-ANALYZER
## Data Collection & Scraping

### Overview
`rss_pipeline.py` scrapes government scheme and policy-related news from RSS feeds, 
detects language, deduplicates entries, and stores them in a local SQLite database 
(`policy_data.db`).
### Sources
| Source | Method | Notes |
|---|---|---|
| BBC Hindi | Direct RSS | Stable |
| Google News - Govt Scheme (Hindi) | Google News RSS search | Query: `sarkari yojana` |
| Google News - Govt Scheme (English) | Google News RSS search | Query: `government scheme india` |
| PIB via Google News | Google News RSS search (`site:pib.gov.in`) | **PIB's own direct RSS feed is broken/returns 0 entries** — this is a workaround that pulls PIB content indirectly through Google News instead |

### Database Schema (`raw_records` table)
| Field | Type | Description |
|---|---|---|
| `id` | TEXT (PK) | MD5 hash of title+link, used for deduplication |
| `source` | TEXT | Which feed the record came from |
| `title` | TEXT | Cleaned article title (HTML stripped) |
| `summary` | TEXT | Cleaned article summary (HTML stripped) |
| `link` | TEXT | Original article URL |
| `published` | TEXT | Publish date as provided by the feed (format varies by source) |
| `language` | TEXT | `hindi`, `hinglish`, or `english` — see limitation below |
| `scraped_at` | TEXT | UTC timestamp of when this script inserted the record |

### Known Limitations
- **Language detection is a simple heuristic**, not a proper NLP classifier: it 
  counts Devanagari characters and checks against a small Hinglish wordlist. It 
  is NOT highly accurate and may misclassify short or ambiguous text. Anyone doing 
  NLP work downstream should treat this as a rough tag, not ground truth.
- **Deduplication is exact-match only** (same title+link hash). Near-duplicate 
  articles (same story, slightly different wording/source) are NOT caught.
- **`published` date format varies by source** — not normalized yet. Needs 
  parsing/standardization before use in any time-based analysis.

### Running it
```
pip install requests beautifulsoup4 feedparser
python rss_pipeline.py
```