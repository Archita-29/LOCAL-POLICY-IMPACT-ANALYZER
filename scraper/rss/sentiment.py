"""
scraper/rss/sentiment.py
------------------------
Facade for Multilingual Policy Sentiment Analyzer.
Delegates to the canonical implementation in ml/sentiment_analyzer.py
to eliminate duplicate lexicon dictionaries and maintain a single source of truth.
"""

import os
import sys
from typing import Dict, Any

# Ensure ml package is accessible on sys.path
_this_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
_parent_root = os.path.abspath(os.path.join(_repo_root, ".."))

for p in [
    os.path.join(_repo_root, "ml"),
    _repo_root,
    os.path.join(_parent_root, "ml"),
    _parent_root,
]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from ml.sentiment_analyzer import predict_sentiment, PolicySentimentAnalyzer, analyzer
except ImportError:
    try:
        from sentiment_analyzer import predict_sentiment, PolicySentimentAnalyzer, analyzer
    except ImportError:
        def predict_sentiment(text: str) -> Dict[str, Any]:
            return {"sentiment_score": 0.0, "sentiment_label": "Neutral", "confidence": 0.5}

        class PolicySentimentAnalyzer:
            def analyze(self, text: str) -> Dict[str, Any]:
                return predict_sentiment(text)

        analyzer = PolicySentimentAnalyzer()

__all__ = ["predict_sentiment", "PolicySentimentAnalyzer", "analyzer"]
