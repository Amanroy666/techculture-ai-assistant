"""
api.py
------
FastAPI-based REST API for the Techculture.ai Service Information Assistant.

Endpoints:
  POST /ask     — Submit a question, get back an answer with sources and tool outputs
  GET  /health  — Health check endpoint
  GET  /rebuild — Rebuild the vector store (for re-indexing after adding new docs)

Run with:
  uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import API_TITLE, API_VERSION
from agent import run_agent
from embeddings import build_vector_store, get_vector_store

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)

# Global vector store reference — loaded once at startup
_vector_store = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Initialize the vector store when the API starts.
    This avoids rebuilding it on every request.
    """
    global _vector_store
    logger.info("Starting up — initializing vector store...")
    try:
        _vector_store = build_vector_store(force_rebuild=False)
        logger.info(f"Vector store ready. Chunks indexed: {_vector_store.count()}")
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        raise RuntimeError(f"Could not start API — vector store init failed: {e}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=(
        "Service Information Assistant for Techculture.ai — "
        "Answers questions about services, pricing, and case studies "
        "using a RAG pipeline grounded in company documents."
    ),
    lifespan=lifespan,
)

# Allow frontend / Streamlit to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The question to ask the service assistant",
        examples=["What AI services do you offer?"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What's the estimated cost for a 3-month digital marketing campaign?"
            }
        }


class SourceCitation(BaseModel):
    file: str
    section: str


class PricingEstimateResponse(BaseModel):
    triggered: bool
    service_type: Optional[str] = None
    duration_months: Optional[int] = None
    min_inr: Optional[int] = None
    max_inr: Optional[int] = None
    min_usd: Optional[int] = None
    max_usd: Optional[int] = None
    notes: Optional[str] = None


class SentimentResponse(BaseModel):
    label: str
    confidence: str
    signals: List[str]


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]
    tools_used: List[str]
    tool_outputs: Dict[str, str]
    sentiment: SentimentResponse
    pricing_estimate: PricingEstimateResponse


# ─────────────────────────────────────────────────────────
# Error Handling
# ─────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    Returns status and how many document chunks are indexed.
    """
    global _vector_store
    if _vector_store is None:
        return {"status": "unhealthy", "reason": "Vector store not initialized"}

    return {
        "status": "healthy",
        "chunks_indexed": _vector_store.count(),
        "api_version": API_VERSION
    }


@app.post("/ask", response_model=AskResponse, tags=["Assistant"])
async def ask_question(request: AskRequest):
    """
    Submit a question to the Techculture.ai Service Assistant.

    The assistant:
    - Retrieves relevant document chunks using semantic search
    - Generates a grounded answer using Gemini
    - Automatically calls the Pricing Estimator tool for pricing questions
    - Runs sentiment analysis on every query
    - Returns the answer with source citations and tool outputs
    """
    global _vector_store

    if _vector_store is None:
        raise HTTPException(
            status_code=503,
            detail="Vector store not initialized. Please try again in a moment."
        )

    query = request.question.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    logger.info(f"Received question: '{query}'")

    try:
        result = run_agent(query, collection=_vector_store)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process your question.")

    return AskResponse(
        question=result["query"],
        answer=result["answer"],
        sources=[SourceCitation(**s) for s in result["sources"]],
        tools_used=result["tools_used"],
        tool_outputs=result["tool_outputs"],
        sentiment=SentimentResponse(**result["sentiment"]),
        pricing_estimate=PricingEstimateResponse(**result["pricing_estimate"])
    )


@app.get("/rebuild", tags=["System"])
async def rebuild_index():
    """
    Rebuild the vector store from scratch.
    Call this after adding new documents to the docs/ folder.

    Warning: This re-indexes all documents and may take a minute.
    """
    global _vector_store
    try:
        logger.info("Rebuilding vector store...")
        _vector_store = build_vector_store(force_rebuild=True)
        return {
            "status": "success",
            "message": "Vector store rebuilt successfully",
            "chunks_indexed": _vector_store.count()
        }
    except Exception as e:
        logger.error(f"Rebuild failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    uvicorn.run("api:app", host=API_HOST, port=API_PORT, reload=True)
