"""
config.py
---------
Central configuration for the Techculture.ai Service Assistant.
All sensitive values are loaded from environment variables via .env.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq (LLM generation) ────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set.\n"
        "Copy .env.example to .env and add your key from https://console.groq.com"
    )

GEMINI_API_KEY = GROQ_API_KEY   # alias kept for backward compat with agent.py imports
GROQ_GENERATION_MODEL = "llama-3.1-8b-instant"
GEMINI_GENERATION_MODEL = GROQ_GENERATION_MODEL   # alias

# ── Document ingestion ────────────────────────────────────
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80

# ── ChromaDB vector store ─────────────────────────────────
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
CHROMA_COLLECTION_NAME = "techculture_docs"
TOP_K_RESULTS = 5

# ── Generation settings ───────────────────────────────────
MAX_OUTPUT_TOKENS = 1024
TEMPERATURE = 0.2

# ── Pricing tool trigger keywords ────────────────────────
PRICING_TRIGGER_KEYWORDS = [
    "cost", "price", "pricing", "estimate", "budget",
    "how much", "quote", "rates", "charges", "fee", "fees",
    "expensive", "affordable", "investment", "spend"
]
