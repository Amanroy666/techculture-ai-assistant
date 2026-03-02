"""
rag_pipeline.py
---------------
Core RAG (Retrieval-Augmented Generation) pipeline.

Takes a user query → retrieves relevant document chunks from ChromaDB
→ constructs a grounded prompt → calls Gemini to generate a final answer
→ returns the answer with source citations.

The answer is always grounded in retrieved context — no hallucinations.
Source citations are always included in the response.
"""

import logging
from typing import List, Dict, Any, Optional

import google.generativeai as genai

from config import (
    GEMINI_API_KEY,
    GEMINI_GENERATION_MODEL,
    TOP_K_RESULTS,
    MAX_OUTPUT_TOKENS,
    TEMPERATURE,
)
from embeddings import search_similar_chunks, get_vector_store

logger = logging.getLogger(__name__)

# Configure Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)


# System prompt — sets the assistant's persona and behavior constraints
SYSTEM_PROMPT = """You are a knowledgeable and helpful assistant for Techculture.ai, 
a technology consulting company. Your job is to answer questions from potential clients 
and internal team members about the company's services, pricing, experience, and expertise.

Important rules you must always follow:
1. Base your answers ONLY on the provided document context. Do not make up information.
2. If the context doesn't contain enough information to answer confidently, say so honestly.
3. Be concise but complete. Avoid unnecessary filler phrases.
4. Use a professional but approachable tone — not robotic, not overly casual.
5. Always include a "Sources" section at the end of your answer listing where the info came from.
6. Format source citations as: "Source: [filename], Section: [section name]"
7. If multiple sources were used, list all of them.

You represent a premium technology company. Every response should reflect that quality."""


def build_rag_prompt(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Construct the full RAG prompt by combining retrieved context with the user query.

    Format:
      [System context]
      [Retrieved document chunks, labeled by source]
      [User question]
    """
    # Build the context block from retrieved chunks
    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_blocks.append(
            f"[Context {i}]\n"
            f"Source: {chunk['source']}, Section: {chunk['section']}\n"
            f"{chunk['text']}"
        )

    context_str = "\n\n---\n\n".join(context_blocks)

    prompt = f"""{SYSTEM_PROMPT}

---

RELEVANT DOCUMENT CONTEXT:
{context_str}

---

USER QUESTION:
{query}

---

Please provide a helpful, accurate answer based on the context above. 
Remember to include source citations at the end of your response."""

    return prompt


def generate_answer(prompt: str) -> str:
    """
    Call Gemini to generate an answer from the RAG prompt.
    Handles basic error cases and returns a clean response string.
    """
    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_GENERATION_MODEL,
            generation_config=genai.GenerationConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=TEMPERATURE,
            )
        )
        response = model.generate_content(prompt)

        # Extract text from response
        if response.text:
            return response.text.strip()
        else:
            logger.warning("Gemini returned an empty response.")
            return "I wasn't able to generate a response. Please try rephrasing your question."

    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        raise RuntimeError(f"Answer generation failed: {str(e)}")


def format_sources(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Deduplicate and format source citations from retrieved chunks.
    Returns a list of unique source dicts with filename and section.
    """
    seen = set()
    sources = []
    for chunk in retrieved_chunks:
        key = (chunk["source"], chunk["section"])
        if key not in seen:
            seen.add(key)
            sources.append({
                "file": chunk["source"],
                "section": chunk["section"]
            })
    return sources


def run_rag_query(
    query: str,
    top_k: int = TOP_K_RESULTS,
    collection=None
) -> Dict[str, Any]:
    """
    Main RAG pipeline function.

    Steps:
    1. Retrieve top_k semantically similar chunks from vector store
    2. Build a grounded prompt combining context + query
    3. Call Gemini to generate the answer
    4. Return answer + sources + metadata

    Returns a dict with keys:
      - answer: str (the generated answer)
      - sources: list of {file, section} dicts
      - retrieved_chunks: raw retrieved chunks (for debugging)
      - query: original query
    """
    logger.info(f"Running RAG query: '{query[:80]}...'")

    # Step 1: Retrieve relevant chunks
    if collection is None:
        collection = get_vector_store()

    retrieved_chunks = search_similar_chunks(
        query=query,
        top_k=top_k,
        collection=collection
    )

    if not retrieved_chunks:
        return {
            "query": query,
            "answer": (
                "I couldn't find relevant information in our knowledge base for your question. "
                "Please try rephrasing, or contact us directly at hello@techculture.ai."
            ),
            "sources": [],
            "retrieved_chunks": []
        }

    # Step 2: Build the RAG prompt
    prompt = build_rag_prompt(query, retrieved_chunks)

    # Step 3: Generate answer with Gemini
    answer = generate_answer(prompt)

    # Step 4: Format sources
    sources = format_sources(retrieved_chunks)

    logger.info(f"Answer generated. Sources used: {[s['file'] for s in sources]}")

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": retrieved_chunks  # useful for debugging/evaluation
    }


if __name__ == "__main__":
    import json
    import logging
    from embeddings import build_vector_store

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # Build vector store if needed
    collection = build_vector_store(force_rebuild=False)

    test_queries = [
        "What AI consulting services do you offer?",
        "Do you have experience with fintech projects?",
        "What is the cost of a 3-month digital marketing campaign?",
    ]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"QUERY: {q}")
        print('='*70)
        result = run_rag_query(q, collection=collection)
        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nSOURCES:")
        for s in result["sources"]:
            print(f"  - {s['file']} (Section: {s['section']})")
