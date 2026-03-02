"""
config.py
---------
Central configuration for the Techculture.ai Service Assistant.
All API keys and model settings are loaded from environment variables.
Never hardcode secrets here — use a .env file locally.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (only in local dev)
load_dotenv()


# ─────────────────────────────────────────────
# Gemini API
# ─────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY not found. Please set it in your .env file or environment."
    )

# Gemini model names
GEMINI_GENERATION_MODEL = "gemini-1.5-flash"       # used for answer generation
GEMINI_EMBEDDING_MODEL = "models/embedding-001"     # used for vector embeddings


# ─────────────────────────────────────────────
# Document Ingestion Settings
# ─────────────────────────────────────────────
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")

# Chunking parameters — tuned for typical consulting/service docs
CHUNK_SIZE = 600          # characters per chunk (roughly 120–150 tokens)
CHUNK_OVERLAP = 80        # overlap between consecutive chunks to preserve context


# ─────────────────────────────────────────────
# Vector Store (ChromaDB)
# ─────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
CHROMA_COLLECTION_NAME = "techculture_docs"

# How many top chunks to retrieve per query
TOP_K_RESULTS = 5


# ─────────────────────────────────────────────
# RAG Generation Settings
# ─────────────────────────────────────────────
MAX_OUTPUT_TOKENS = 1024
TEMPERATURE = 0.2          # low temperature → factual, consistent answers


# ─────────────────────────────────────────────
# Agent / Tool Settings
# ─────────────────────────────────────────────
SENTIMENT_THRESHOLD = 0.0  # include sentiment in response (always, for now)

# Pricing estimator: these keywords trigger the pricing tool
PRICING_TRIGGER_KEYWORDS = [
    "cost", "price", "pricing", "estimate", "budget",
    "how much", "quote", "rates", "charges", "fee", "fees",
    "expensive", "affordable", "investment", "spend"
]


# ─────────────────────────────────────────────
# FastAPI Settings
# ─────────────────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "Techculture.ai Service Assistant API"
API_VERSION = "1.0.0"
