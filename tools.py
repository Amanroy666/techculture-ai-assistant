"""
tools.py
--------
Standalone tools that the AI agent can call autonomously based on query intent.

Tool 1 - Pricing Estimator:
  Accepts a service type and duration, returns a cost estimate range.
  The agent calls this when it detects pricing-related intent in the query.

Tool 2 - Sentiment Analyzer:
  Classifies user query as Positive / Negative / Neutral based on tone signals.
  Helps tailor the response tone (e.g., reassuring for frustrated queries).
"""

import re
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
# Data Classes for Tool Outputs
# ─────────────────────────────────────────────────────────

@dataclass
class PricingEstimate:
    service_type: str
    duration_months: int
    min_price_inr: int
    max_price_inr: int
    min_price_usd: int
    max_price_usd: int
    notes: str
    triggered: bool = True


@dataclass
class SentimentResult:
    label: str          # "Positive", "Negative", or "Neutral"
    confidence: str     # "High", "Medium", "Low"
    signals: list       # keywords that influenced the classification
    triggered: bool = True


# ─────────────────────────────────────────────────────────
# Tool 1: Pricing Estimator
# ─────────────────────────────────────────────────────────

# Pricing database (INR ranges, then converted at ~83 INR/USD)
PRICING_DB = {
    "ai_consulting": {
        "base_inr": (350000, 600000),
        "monthly_rate_inr": (100000, 300000),
        "notes": "Includes AI readiness assessment and strategy roadmap."
    },
    "ml_development": {
        "base_inr": (400000, 1000000),
        "monthly_rate_inr": (400000, 1000000),
        "notes": "Custom ML model development. Price scales with complexity."
    },
    "llm_rag": {
        "base_inr": (600000, 2000000),
        "monthly_rate_inr": (200000, 500000),
        "notes": "LLM integration, RAG systems, AI-powered apps."
    },
    "digital_marketing": {
        "base_inr": (75000, 200000),
        "monthly_rate_inr": (75000, 200000),
        "notes": "Full-stack digital marketing. Excludes ad spend."
    },
    "seo": {
        "base_inr": (35000, 140000),
        "monthly_rate_inr": (35000, 140000),
        "notes": "Organic SEO — technical, on-page, and off-page."
    },
    "ppc": {
        "base_inr": (40000, 100000),
        "monthly_rate_inr": (40000, 100000),
        "notes": "Management fee only. Ad spend budget is additional."
    },
    "web_development": {
        "base_inr": (500000, 1500000),
        "monthly_rate_inr": (300000, 600000),
        "notes": "Web app development. MVP packages start lower."
    },
    "mobile_development": {
        "base_inr": (800000, 3500000),
        "monthly_rate_inr": (400000, 800000),
        "notes": "Flutter/React Native cross-platform or native iOS/Android."
    },
    "data_engineering": {
        "base_inr": (600000, 2000000),
        "monthly_rate_inr": (150000, 400000),
        "notes": "ETL pipelines, data warehouses, real-time streaming."
    },
    "mlops": {
        "base_inr": (800000, 2500000),
        "monthly_rate_inr": (200000, 400000),
        "notes": "MLOps pipeline, model monitoring, CI/CD for ML."
    },
}

# Map common query terms to internal service keys
SERVICE_KEYWORD_MAP = {
    "ai consulting": "ai_consulting",
    "consulting": "ai_consulting",
    "ai strategy": "ai_consulting",
    "machine learning": "ml_development",
    "ml": "ml_development",
    "custom model": "ml_development",
    "llm": "llm_rag",
    "rag": "llm_rag",
    "chatbot": "llm_rag",
    "generative ai": "llm_rag",
    "genai": "llm_rag",
    "digital marketing": "digital_marketing",
    "marketing": "digital_marketing",
    "seo": "seo",
    "search engine": "seo",
    "ppc": "ppc",
    "paid ads": "ppc",
    "google ads": "ppc",
    "web development": "web_development",
    "web app": "web_development",
    "website": "web_development",
    "mobile app": "mobile_development",
    "mobile": "mobile_development",
    "app development": "mobile_development",
    "flutter": "mobile_development",
    "data engineering": "data_engineering",
    "pipeline": "data_engineering",
    "data pipeline": "data_engineering",
    "mlops": "mlops",
    "model deployment": "mlops",
}


def detect_service_from_query(query: str) -> Optional[str]:
    """
    Heuristic: scan the query for known service keywords.
    Returns the internal service key or None if not detected.
    """
    query_lower = query.lower()
    for keyword, service_key in SERVICE_KEYWORD_MAP.items():
        if keyword in query_lower:
            return service_key
    return None


def estimate_price(
    service_type: Optional[str],
    duration_months: int = 1,
    raw_query: str = ""
) -> PricingEstimate:
    """
    Return a pricing estimate for a given service and duration.

    If service_type is None, attempt to detect it from raw_query.
    If still not found, return a general estimate.
    """
    # Try to auto-detect service from query if not explicitly given
    if not service_type and raw_query:
        service_type = detect_service_from_query(raw_query)

    if not service_type or service_type not in PRICING_DB:
        # Generic fallback
        return PricingEstimate(
            service_type="general",
            duration_months=duration_months,
            min_price_inr=350000 * duration_months,
            max_price_inr=2000000 * duration_months,
            min_price_usd=4200 * duration_months,
            max_price_usd=24000 * duration_months,
            notes=(
                "This is a general estimate. The actual cost depends heavily on the "
                "specific service, scope, and complexity. Please contact us at "
                "hello@techculture.ai for a tailored quote."
            )
        )

    pricing = PRICING_DB[service_type]
    monthly_min, monthly_max = pricing["monthly_rate_inr"]

    total_min_inr = monthly_min * duration_months
    total_max_inr = monthly_max * duration_months

    # Convert to USD (approximate)
    total_min_usd = round(total_min_inr / 83)
    total_max_usd = round(total_max_inr / 83)

    logger.info(f"Pricing estimate triggered for: {service_type}, {duration_months} months")

    return PricingEstimate(
        service_type=service_type.replace("_", " ").title(),
        duration_months=duration_months,
        min_price_inr=total_min_inr,
        max_price_inr=total_max_inr,
        min_price_usd=total_min_usd,
        max_price_usd=total_max_usd,
        notes=pricing["notes"]
    )


def format_pricing_output(estimate: PricingEstimate) -> str:
    """Format a PricingEstimate into a clean human-readable string."""
    return (
        f"📊 **Pricing Estimate** ({estimate.service_type})\n"
        f"  • Duration: {estimate.duration_months} month(s)\n"
        f"  • Estimated Range (INR): ₹{estimate.min_price_inr:,} – ₹{estimate.max_price_inr:,}\n"
        f"  • Estimated Range (USD): ${estimate.min_price_usd:,} – ${estimate.max_price_usd:,}\n"
        f"  • Note: {estimate.notes}"
    )


# ─────────────────────────────────────────────────────────
# Tool 2: Sentiment Analyzer
# ─────────────────────────────────────────────────────────

POSITIVE_SIGNALS = [
    "interested", "excited", "great", "love", "perfect", "impressed",
    "looking forward", "happy", "excellent", "thank", "appreciate",
    "good", "wonderful", "amazing", "fantastic", "curious", "eager"
]

NEGATIVE_SIGNALS = [
    "frustrated", "disappointed", "unhappy", "angry", "bad", "poor",
    "terrible", "not satisfied", "problem", "issue", "concern",
    "confused", "worried", "doubt", "skeptical", "expensive", "too costly",
    "difficult", "complicated", "slow", "delayed", "failed"
]

NEUTRAL_SIGNALS = [
    "what", "how", "when", "where", "which", "who", "can you", "do you",
    "tell me", "explain", "describe", "information", "details"
]


def analyze_sentiment(text: str) -> SentimentResult:
    """
    Simple rule-based sentiment analysis on user query.
    Counts positive and negative signal words to classify sentiment.
    """
    text_lower = text.lower()

    positive_found = [w for w in POSITIVE_SIGNALS if w in text_lower]
    negative_found = [w for w in NEGATIVE_SIGNALS if w in text_lower]

    pos_score = len(positive_found)
    neg_score = len(negative_found)

    if pos_score > neg_score:
        label = "Positive"
        confidence = "High" if pos_score >= 2 else "Medium"
        signals = positive_found
    elif neg_score > pos_score:
        label = "Negative"
        confidence = "High" if neg_score >= 2 else "Medium"
        signals = negative_found
    else:
        label = "Neutral"
        confidence = "High"
        signals = []

    return SentimentResult(
        label=label,
        confidence=confidence,
        signals=signals
    )


def format_sentiment_output(result: SentimentResult) -> str:
    """Format sentiment result as a short string."""
    signal_str = f" (signals: {', '.join(result.signals[:3])})" if result.signals else ""
    return f"🎭 **Query Sentiment**: {result.label} (confidence: {result.confidence}){signal_str}"


if __name__ == "__main__":
    # Quick test of both tools
    test_queries = [
        ("digital marketing", 3),
        ("seo", 6),
        ("ai consulting", 2),
        ("machine learning", 4),
    ]
    print("=== Pricing Estimator Tests ===")
    for service, months in test_queries:
        est = estimate_price(service, months)
        print(format_pricing_output(est))
        print()

    print("=== Sentiment Analyzer Tests ===")
    test_sentiments = [
        "I'm really excited about your AI services, they sound amazing!",
        "I'm frustrated with how expensive everything seems to be.",
        "Can you tell me what digital marketing services you offer?"
    ]
    for q in test_sentiments:
        result = analyze_sentiment(q)
        print(f"Query: {q[:60]}...")
        print(format_sentiment_output(result))
        print()
