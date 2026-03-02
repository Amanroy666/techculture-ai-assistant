"""
embeddings.py
-------------
Handles vector embedding generation using Google's embedding-001 model
and storage/retrieval via ChromaDB (local persistent vector store).

Key functions:
  - build_vector_store(): Ingest all docs, embed them, store in Chroma
  - get_vector_store(): Load existing Chroma collection
  - search_similar_chunks(): Semantic search against stored embeddings
"""

import logging
import time
from typing import List, Dict, Any, Optional

import google.generativeai as genai
import chromadb
from chromadb.config import Settings

from config import (
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    TOP_K_RESULTS,
    DOCS_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from ingestion import ingest_all_documents

logger = logging.getLogger(__name__)

# Configure Gemini SDK once at module level
genai.configure(api_key=GEMINI_API_KEY)


def embed_text(text: str, task_type: str = "retrieval_document") -> List[float]:
    """
    Generate an embedding vector for a single text string using Gemini.

    task_type options (affects how Gemini optimizes the embedding):
      - "retrieval_document"  : for documents being indexed
      - "retrieval_query"     : for user queries being searched
    """
    try:
        result = genai.embed_content(
            model=GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type=task_type
        )
        return result["embedding"]
    except Exception as e:
        logger.error(f"Embedding failed for text snippet: {text[:100]}... Error: {e}")
        raise


def embed_batch(
    texts: List[str],
    task_type: str = "retrieval_document",
    batch_size: int = 20,
    sleep_between_batches: float = 1.0
) -> List[List[float]]:
    """
    Embed a list of texts in batches to stay within API rate limits.
    Gemini's free tier has rate limits so we sleep between batches.
    """
    all_embeddings = []
    total = len(texts)

    for i in range(0, total, batch_size):
        batch = texts[i: i + batch_size]
        logger.info(f"Embedding batch {i // batch_size + 1} / {(total + batch_size - 1) // batch_size} ({len(batch)} items)")

        for text in batch:
            emb = embed_text(text, task_type=task_type)
            all_embeddings.append(emb)

        # Small sleep to be kind to the API rate limits
        if i + batch_size < total:
            time.sleep(sleep_between_batches)

    return all_embeddings


def get_chroma_client() -> chromadb.Client:
    """Return a persistent ChromaDB client."""
    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    return client


def build_vector_store(force_rebuild: bool = False) -> chromadb.Collection:
    """
    Full pipeline:
      1. Load and chunk all documents from docs/
      2. Generate embeddings via Gemini
      3. Store in ChromaDB with metadata

    If the collection already exists and force_rebuild=False, skip re-indexing.
    Set force_rebuild=True to re-ingest after adding new documents.
    """
    client = get_chroma_client()

    # Check if collection already exists
    existing_collections = [c.name for c in client.list_collections()]

    if CHROMA_COLLECTION_NAME in existing_collections and not force_rebuild:
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
        logger.info(
            f"Vector store already exists with {collection.count()} chunks. "
            "Skipping rebuild. Use force_rebuild=True to re-index."
        )
        return collection

    # Delete existing collection if force rebuild
    if CHROMA_COLLECTION_NAME in existing_collections:
        client.delete_collection(name=CHROMA_COLLECTION_NAME)
        logger.info("Deleted existing collection for rebuild.")

    # Create fresh collection
    collection = client.create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # cosine similarity for semantic search
    )

    # Ingest documents
    logger.info("Starting document ingestion...")
    chunks = ingest_all_documents(DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP)

    if not chunks:
        raise ValueError("No chunks found. Check that docs/ folder has .md or .txt files.")

    # Generate embeddings
    logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_batch(texts, task_type="retrieval_document")

    # Store in ChromaDB
    logger.info("Storing embeddings in ChromaDB...")
    collection.add(
        ids=[f"{chunk['source']}__chunk_{chunk['chunk_index']}" for chunk in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "source": chunk["source"],
                "section": chunk["section"],
                "chunk_index": chunk["chunk_index"]
            }
            for chunk in chunks
        ]
    )

    logger.info(f"Vector store built successfully. {collection.count()} chunks indexed.")
    return collection


def get_vector_store() -> chromadb.Collection:
    """
    Load existing ChromaDB collection.
    Raises an error if the collection doesn't exist yet — run build_vector_store() first.
    """
    client = get_chroma_client()
    existing = [c.name for c in client.list_collections()]

    if CHROMA_COLLECTION_NAME not in existing:
        raise RuntimeError(
            "Vector store not found. Run build_vector_store() or "
            "'python embeddings.py --build' to index documents first."
        )

    return client.get_collection(name=CHROMA_COLLECTION_NAME)


def search_similar_chunks(
    query: str,
    top_k: int = TOP_K_RESULTS,
    collection: Optional[chromadb.Collection] = None
) -> List[Dict[str, Any]]:
    """
    Semantic search: embed the query and find top_k most similar chunks.

    Returns a list of result dicts, each with:
      - text: chunk content
      - source: document filename
      - section: section heading
      - distance: similarity distance (lower = more similar for cosine)
    """
    if collection is None:
        collection = get_vector_store()

    # Embed the query with retrieval_query task type
    query_embedding = embed_text(query, task_type="retrieval_query")

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    # Flatten and structure results
    retrieved = []
    for i, doc_text in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        retrieved.append({
            "text": doc_text,
            "source": metadata.get("source", "unknown"),
            "section": metadata.get("section", "General"),
            "distance": round(distance, 4)
        })

    logger.info(f"Retrieved {len(retrieved)} chunks for query: '{query[:60]}...'")
    return retrieved


if __name__ == "__main__":
    import argparse
    import json

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Build or test the vector store")
    parser.add_argument("--build", action="store_true", help="Build the vector store from docs/")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild even if it exists")
    parser.add_argument("--search", type=str, default=None, help="Test a search query")
    args = parser.parse_args()

    if args.build or args.rebuild:
        print("Building vector store...")
        build_vector_store(force_rebuild=args.rebuild)
        print("Done.")

    if args.search:
        print(f"\nSearching for: '{args.search}'")
        results = search_similar_chunks(args.search)
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] Source: {r['source']} | Section: {r['section']} | Distance: {r['distance']}")
            print(f"     {r['text'][:300]}...")
