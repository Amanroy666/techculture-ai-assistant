"""
embeddings.py
-------------
Vector embedding using ChromaDB's built-in local embedding function
(all-MiniLM-L6-v2 via onnxruntime — no external API needed, completely free).
Gemini API is only used for answer generation, not for embeddings.
"""

import logging
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    TOP_K_RESULTS,
    DOCS_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from ingestion import ingest_all_documents

logger = logging.getLogger(__name__)

# Local embedding function — uses all-MiniLM-L6-v2 via onnxruntime
# Completely free, no API key needed, runs entirely on your server
_embedding_fn = DefaultEmbeddingFunction()


def get_chroma_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False)
    )


def build_vector_store(force_rebuild: bool = False) -> chromadb.Collection:
    """
    Full indexing pipeline:
    1. Load and chunk all docs from docs/
    2. Generate embeddings using local all-MiniLM-L6-v2 model
    3. Store in ChromaDB
    """
    client = get_chroma_client()
    existing = [c.name for c in client.list_collections()]

    if CHROMA_COLLECTION_NAME in existing and not force_rebuild:
        collection = client.get_collection(
            name=CHROMA_COLLECTION_NAME,
            embedding_function=_embedding_fn
        )
        logger.info(f"Vector store already exists with {collection.count()} chunks. Skipping rebuild.")
        return collection

    if CHROMA_COLLECTION_NAME in existing:
        client.delete_collection(name=CHROMA_COLLECTION_NAME)
        logger.info("Deleted existing collection for rebuild.")

    collection = client.create_collection(
        name=CHROMA_COLLECTION_NAME,
        embedding_function=_embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

    logger.info("Starting document ingestion...")
    chunks = ingest_all_documents(DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP)
    if not chunks:
        raise ValueError("No chunks found. Check that docs/ folder has .md or .txt files.")

    logger.info(f"Generating local embeddings for {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    ids = [f"{c['source']}__chunk_{c['chunk_index']}" for c in chunks]
    metadatas = [
        {"source": c["source"], "section": c["section"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    # ChromaDB handles embedding automatically via the embedding_function
    collection.add(ids=ids, documents=texts, metadatas=metadatas)

    logger.info(f"Vector store built. {collection.count()} chunks indexed.")
    return collection


def get_vector_store() -> chromadb.Collection:
    """Load existing ChromaDB collection."""
    client = get_chroma_client()
    existing = [c.name for c in client.list_collections()]
    if CHROMA_COLLECTION_NAME not in existing:
        raise RuntimeError("Vector store not found. Run: python3 embeddings.py --build")
    return client.get_collection(
        name=CHROMA_COLLECTION_NAME,
        embedding_function=_embedding_fn
    )


def search_similar_chunks(
    query: str,
    top_k: int = TOP_K_RESULTS,
    collection: Optional[chromadb.Collection] = None
) -> List[Dict[str, Any]]:
    """Semantic search: find top_k most similar chunks to the query."""
    if collection is None:
        collection = get_vector_store()

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []
    for i, doc_text in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        retrieved.append({
            "text": doc_text,
            "source": metadata.get("source", "unknown"),
            "section": metadata.get("section", "General"),
            "distance": round(results["distances"][0][i], 4)
        })

    logger.info(f"Retrieved {len(retrieved)} chunks for query.")
    return retrieved


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="Build vector store")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild")
    parser.add_argument("--search", type=str, default=None, help="Test a search query")
    args = parser.parse_args()

    if args.build or args.rebuild:
        print("Building vector store (using local embeddings — no API needed)...")
        build_vector_store(force_rebuild=args.rebuild)
        print("Done.")

    if args.search:
        results = search_similar_chunks(args.search)
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['source']} | {r['section']} | dist={r['distance']}")
            print(f"     {r['text'][:250]}...")
