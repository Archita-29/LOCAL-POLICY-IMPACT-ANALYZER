import feedparser

feeds = [
    ("TOI", "https://timesofindia.indiatimes.com/rss_toinews.cms"),
    ("Navbharat Times", "https://navbharattimes.indiatimes.com/rss.cms"),
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for name, url in feeds:
    f = feedparser.parse(url, request_headers=headers)
    print(name, len(f.entries), f.entries[0].title if f.entries else "NO ENTRIES")