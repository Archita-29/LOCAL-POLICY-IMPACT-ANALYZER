"""
ml/sentiment_analyzer.py
-------------------------
Multilingual Policy News Sentiment Analyzer for Hindi, English, and Hinglish.

Analyzes text from scraped government scheme news articles, evaluates polarity
considering policy-specific positive and negative vocabulary (subsidies, relief,
delays, scams, protests), and outputs:
  - sentiment_score: float in range [-1.0, 1.0]
  - sentiment_label: "Positive", "Neutral", or "Negative"
  - confidence: float in range [0.0, 1.0]
"""

import re
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Policy-specific Lexicons (Hindi, English, Hinglish)
# ---------------------------------------------------------------------------

POSITIVE_TERMS_EN = {
    "subsidy": 1.5,
    "relief": 1.8,
    "benefit": 1.4,
    "beneficiary": 1.2,
    "sanctioned": 1.3,
    "approved": 1.4,
    "boost": 1.5,
    "success": 1.8,
    "successful": 1.7,
    "free": 1.3,
    "financial assistance": 1.6,
    "cashless": 1.4,
    "empowerment": 1.6,
    "progress": 1.5,
    "credited": 1.5,
    "growth": 1.3,
    "achievement": 1.7,
    "milestone": 1.5,
    "effective": 1.4,
    "hails": 1.4,
    "welcomed": 1.5,
    "allocated": 1.2,
    "improved": 1.5,
    "reforms": 1.3,
    "grant": 1.4,
    "support": 1.3,
    "expansion": 1.3,
}

NEGATIVE_TERMS_EN = {
    "delay": -1.5,
    "delayed": -1.5,
    "protest": -1.6,
    "strike": -1.4,
    "scam": -2.0,
    "fraud": -2.0,
    "complaint": -1.4,
    "slow": -1.2,
    "denied": -1.6,
    "deprived": -1.7,
    "unfulfilled": -1.6,
    "poor": -1.3,
    "death": -1.8,
    "murder": -2.0,
    "crime": -1.8,
    "violence": -1.8,
    "failed": -1.7,
    "failure": -1.7,
    "cut": -1.2,
    "cancelled": -1.5,
    "crisis": -1.7,
    "loss": -1.4,
    "damage": -1.4,
    "toothless": -1.6,
    "controversy": -1.5,
    "bhaag gaya": -1.6,
}

POSITIVE_TERMS_HI = {
    "सब्सिडी": 1.6,
    "राहत": 1.8,
    "लाभ": 1.5,
    "फायदा": 1.5,
    "सहायता": 1.5,
    "मंजूरी": 1.4,
    "स्वीकृत": 1.4,
    "खुशी": 1.7,
    "बजट आवंटित": 1.4,
    "सफल": 1.7,
    "सफलता": 1.7,
    "मुफ्त": 1.5,
    "निशुल्क": 1.5,
    "खाते में": 1.3,
    "पेंशन": 1.2,
    "आवास": 1.2,
    "सुविधा": 1.4,
    "सशक्तिकरण": 1.6,
    "उन्नति": 1.5,
    "विकास": 1.4,
    "उपलब्धि": 1.6,
    "गारंटी": 1.4,
    "धनराशि": 1.2,
    "प्रोत्साहन": 1.4,
}

NEGATIVE_TERMS_HI = {
    "देरी": -1.5,
    "घोटाला": -2.0,
    "धांधली": -1.8,
    "परेशानी": -1.5,
    "समस्या": -1.4,
    "विरोध": -1.6,
    "हड़ताल": -1.5,
    "वंचित": -1.7,
    "शिकायत": -1.4,
    "कमी": -1.3,
    "बर्बादी": -1.7,
    "नुकसान": -1.5,
    "हत्या": -2.0,
    "अपराध": -1.8,
    "हिंसा": -1.8,
    "ठगी": -1.8,
    "कठिनाई": -1.4,
    "अस्वीकार": -1.6,
    "काट": -1.2,
    "रुकावट": -1.4,
}


class PolicySentimentAnalyzer:
    """
    Multilingual rule-and-lexicon sentiment model optimized for policy/governance news.
    """

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a given text.
        Returns:
            dict with sentiment_score (-1.0 to 1.0), sentiment_label ("Positive", "Neutral", "Negative"),
            and confidence.
        """
        if not text:
            return {"sentiment_score": 0.0, "sentiment_label": "Neutral", "confidence": 0.5}

        text_clean = text.lower()
        score = 0.0
        matches_pos = 0
        matches_neg = 0

        # English matches
        for word, weight in POSITIVE_TERMS_EN.items():
            if re.search(r"\b" + re.escape(word) + r"\b", text_clean):
                score += weight
                matches_pos += 1

        for word, weight in NEGATIVE_TERMS_EN.items():
            if re.search(r"\b" + re.escape(word) + r"\b", text_clean):
                score += weight
                matches_neg += 1

        # Hindi matches
        for word, weight in POSITIVE_TERMS_HI.items():
            if word in text:
                score += weight
                matches_pos += 1

        for word, weight in NEGATIVE_TERMS_HI.items():
            if word in text:
                score += weight
                matches_neg += 1

        total_matches = matches_pos + matches_neg

        # Normalize score into [-1.0, 1.0]
        if total_matches > 0:
            raw_score = score / (total_matches * 1.5)
            norm_score = max(-1.0, min(1.0, raw_score))
        else:
            norm_score = 0.0

        # Classify label
        if norm_score >= 0.15:
            label = "Positive"
        elif norm_score <= -0.15:
            label = "Negative"
        else:
            label = "Neutral"

        confidence = min(0.95, 0.5 + (abs(norm_score) * 0.45) if total_matches > 0 else 0.5)

        return {
            "sentiment_score": round(norm_score, 2),
            "sentiment_label": label,
            "confidence": round(confidence, 2),
            "pos_matches": matches_pos,
            "neg_matches": matches_neg,
        }


# Global instance
analyzer = PolicySentimentAnalyzer()


def predict_sentiment(text: str) -> Dict[str, Any]:
    return analyzer.analyze(text)


analyze_text = predict_sentiment


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    test_samples = [
        "पीएम किसान योजना के तहत किसानों के खाते में ₹2000 की नई किस्त भेजी गई, मिली बड़ी राहत",
        "सोयाबीन की फसल पर किसान ने चलाया ट्रैक्टर, नुकसान से परेशान होकर उठाया कदम",
        "Ayushman Bharat has improved hospital accessibility by 35% with free treatment for vulnerable families",
        "Verification process for the scheme has faced severe delay, farmers protesting against slow administration",
        "Government announced new scheme for farmers with 80% subsidy on agricultural equipment",
    ]
    for s in test_samples:
        res = predict_sentiment(s)
        print(f"[{res['sentiment_label']:8s}] ({res['sentiment_score']:+.2f}) {s[:70]}...")
