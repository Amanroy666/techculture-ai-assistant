"""
agent.py
--------
Orchestration layer that wraps the RAG pipeline with agentic behaviour.

The agent autonomously decides:
  1. Whether the query needs a pricing estimate (calls PricingEstimator tool)
  2. Runs sentiment analysis on every query (informs response tone)
  3. Runs the RAG pipeline to get the document-grounded answer
  4. Combines all outputs into a structured final response

No hardcoded decision logic — the agent uses keyword analysis and 
RAG context together to determine tool usage. This is a pragmatic 
implementation of agentic behaviour that is transparent and debuggable.
"""

import re
import logging
from typing import Optional, Dict, Any, Tuple

import chromadb

from config import PRICING_TRIGGER_KEYWORDS
from rag_pipeline import run_rag_query
from tools import (
    analyze_sentiment,
    estimate_price,
    detect_service_from_query,
    format_pricing_output,
    format_sentiment_output,
    PricingEstimate,
    SentimentResult,
)
from embeddings import get_vector_store, build_vector_store

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
# Agent Decision Logic
# ─────────────────────────────────────────────────────────

def should_call_pricing_tool(query: str) -> bool:
    """
    Decide whether the pricing estimator should be called.
    Returns True if the query contains pricing-intent keywords.
    """
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in PRICING_TRIGGER_KEYWORDS)


def extract_duration_from_query(query: str) -> int:
    """
    Try to extract a duration (in months) from the user's query.
    Looks for patterns like "3 months", "6-month", "for a year" etc.
    Defaults to 1 month if nothing found.
    """
    # Pattern: "3 months", "three months", "6-month"
    month_pattern = re.search(r'(\d+)\s*[\-\s]?month', query.lower())
    if month_pattern:
        return int(month_pattern.group(1))

    # Pattern: "a year", "one year"
    if "year" in query.lower():
        year_match = re.search(r'(\d+)\s*year', query.lower())
        return int(year_match.group(1)) * 12 if year_match else 12

    # "a quarter", "quarterly"
    if "quarter" in query.lower():
        return 3

    # "half year", "6 months", "half a year"
    if "half year" in query.lower() or "half a year" in query.lower():
        return 6

    return 1  # default


# ─────────────────────────────────────────────────────────
# Main Agent Function
# ─────────────────────────────────────────────────────────

def run_agent(
    query: str,
    collection: Optional[chromadb.Collection] = None
) -> Dict[str, Any]:
    """
    Main agent entry point.

    Orchestration flow:
    1. Sentiment Analysis (always runs)
    2. Check if pricing tool should be called → call if yes
    3. Run RAG pipeline for document-grounded answer
    4. Combine and return all outputs

    Returns a structured dict with:
      - query: original user question
      - answer: grounded LLM answer from RAG
      - sources: list of {file, section} citations
      - tools_used: list of tool names that were invoked
      - tool_outputs: dict of tool name → formatted output string
      - sentiment: sentiment analysis result dict
    """
    logger.info(f"Agent received query: '{query}'")
    tools_used = []
    tool_outputs = {}

    # ── Step 1: Sentiment Analysis ──────────────────────────────
    sentiment_result: SentimentResult = analyze_sentiment(query)
    tools_used.append("SentimentAnalyzer")
    tool_outputs["SentimentAnalyzer"] = format_sentiment_output(sentiment_result)
    logger.info(f"Sentiment: {sentiment_result.label} ({sentiment_result.confidence})")

    # ── Step 2: Pricing Estimator (conditional) ──────────────────
    pricing_estimate: Optional[PricingEstimate] = None

    if should_call_pricing_tool(query):
        logger.info("Pricing intent detected — calling PricingEstimator tool")

        # Try to detect service type and duration from the query
        detected_service = detect_service_from_query(query)
        detected_duration = extract_duration_from_query(query)

        pricing_estimate = estimate_price(
            service_type=detected_service,
            duration_months=detected_duration,
            raw_query=query
        )
        tools_used.append("PricingEstimator")
        tool_outputs["PricingEstimator"] = format_pricing_output(pricing_estimate)
        logger.info(f"Pricing estimated for: {pricing_estimate.service_type}, {pricing_estimate.duration_months} months")
    else:
        logger.info("No pricing intent detected — skipping PricingEstimator")

    # ── Step 3: RAG Pipeline ─────────────────────────────────────
    if collection is None:
        try:
            collection = get_vector_store()
        except RuntimeError:
            logger.warning("Vector store not found. Building now...")
            collection = build_vector_store()

    rag_result = run_rag_query(query, collection=collection)

    # ── Step 4: Assemble Final Response ──────────────────────────
    response = {
        "query": query,
        "answer": rag_result["answer"],
        "sources": rag_result["sources"],
        "tools_used": tools_used,
        "tool_outputs": tool_outputs,
        "sentiment": {
            "label": sentiment_result.label,
            "confidence": sentiment_result.confidence,
            "signals": sentiment_result.signals,
        },
        # Include pricing in a structured way for easy API consumption
        "pricing_estimate": {
            "triggered": bool(pricing_estimate),
            "service_type": pricing_estimate.service_type if pricing_estimate else None,
            "duration_months": pricing_estimate.duration_months if pricing_estimate else None,
            "min_inr": pricing_estimate.min_price_inr if pricing_estimate else None,
            "max_inr": pricing_estimate.max_price_inr if pricing_estimate else None,
            "min_usd": pricing_estimate.min_price_usd if pricing_estimate else None,
            "max_usd": pricing_estimate.max_price_usd if pricing_estimate else None,
            "notes": pricing_estimate.notes if pricing_estimate else None,
        } if pricing_estimate else {"triggered": False},
    }

    logger.info(f"Agent response assembled. Tools used: {tools_used}")
    return response


def format_agent_response_for_display(response: Dict[str, Any]) -> str:
    """
    Format the agent's structured response dict into a clean, readable string.
    Used by CLI and Streamlit interfaces.
    """
    lines = []
    lines.append(f"**Question:** {response['query']}\n")
    lines.append(f"**Answer:**\n{response['answer']}\n")

    # Sources
    if response["sources"]:
        lines.append("\n**Sources:**")
        for s in response["sources"]:
            lines.append(f"  • {s['file']} — Section: {s['section']}")

    # Tool outputs
    if response.get("tool_outputs"):
        lines.append("\n**Agent Tools Used:**")
        for tool_name, output in response["tool_outputs"].items():
            lines.append(f"\n{output}")

    return "\n".join(lines)


if __name__ == "__main__":
    import json
    import logging
    from embeddings import build_vector_store

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    print("Initializing vector store...")
    collection = build_vector_store(force_rebuild=False)

    test_queries = [
        "What AI services do you offer?",
        "Do you have experience with fintech projects?",
        "What's the estimated cost for a 3-month digital marketing campaign?",
        "How much does a 6-month ML development project cost?",
        "I'm really frustrated, I can't find pricing information anywhere!",
        "Do you handle data engineering projects?",
    ]

    for query in test_queries:
        print(f"\n{'='*70}")
        response = run_agent(query, collection=collection)
        print(format_agent_response_for_display(response))
