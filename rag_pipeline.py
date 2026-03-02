"""
rag_pipeline.py - Uses Groq (Llama 3.1) for answer generation. Fast and free.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from config import TOP_K_RESULTS, MAX_OUTPUT_TOKENS, TEMPERATURE
from embeddings import search_similar_chunks, get_vector_store

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GENERATION_MODEL = "llama-3.1-8b-instant"   # fast, free, capable
_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a helpful assistant for Techculture.ai, a technology consulting company.
Answer questions about services, pricing, and past projects.
Rules:
1. Answer ONLY from the provided document context.
2. If context lacks the answer, say so and suggest contacting hello@techculture.ai.
3. Be concise and professional.
4. Always end with Sources: Source: [filename], Section: [section name]"""

def build_rag_prompt(query, chunks):
    ctx = "\n\n---\n\n".join(
        f"[Context {i+1}]\nSource: {c['source']}, Section: {c['section']}\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    return f"DOCUMENT CONTEXT:\n{ctx}\n\nUSER QUESTION: {query}\n\nAnswer based only on the context above, then list your sources."

def generate_answer(prompt):
    try:
        r = _client.chat.completions.create(
            model=GENERATION_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=TEMPERATURE,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        raise RuntimeError(f"Answer generation failed: {str(e)}")

def format_sources(chunks):
    seen, sources = set(), []
    for c in chunks:
        k = (c["source"], c["section"])
        if k not in seen:
            seen.add(k)
            sources.append({"file": c["source"], "section": c["section"]})
    return sources

def run_rag_query(query, top_k=TOP_K_RESULTS, collection=None):
    if collection is None:
        collection = get_vector_store()
    chunks = search_similar_chunks(query=query, top_k=top_k, collection=collection)
    if not chunks:
        return {"query": query, "answer": "No relevant info found. Contact hello@techculture.ai.", "sources": [], "retrieved_chunks": []}
    answer = generate_answer(build_rag_prompt(query, chunks))
    return {"query": query, "answer": answer, "sources": format_sources(chunks), "retrieved_chunks": chunks}
