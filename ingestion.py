"""
ingestion.py
------------
Handles loading Markdown/TXT documents from the docs/ folder,
splitting them into overlapping chunks for semantic retrieval,
and returning structured chunk objects with metadata.

Each chunk carries:
  - text: the actual content
  - source: filename
  - section: best-guess section heading (extracted from nearby H2/H3 headings)
  - chunk_index: position within the source document
"""

import os
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def load_documents(docs_dir: str) -> List[Dict[str, Any]]:
    """
    Walk through docs_dir and load all .md and .txt files.
    Returns a list of raw document dicts with keys: filename, content.
    """
    documents = []
    supported_extensions = (".md", ".txt")

    if not os.path.exists(docs_dir):
        raise FileNotFoundError(f"Docs directory not found: {docs_dir}")

    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith(supported_extensions):
            continue

        filepath = os.path.join(docs_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                logger.warning(f"Skipping empty file: {filename}")
                continue

            documents.append({
                "filename": filename,
                "filepath": filepath,
                "content": content
            })
            logger.info(f"Loaded document: {filename} ({len(content)} chars)")

        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")

    logger.info(f"Total documents loaded: {len(documents)}")
    return documents


def _extract_section_for_position(text: str, position: int) -> str:
    """
    Given a character position in the text, find the most recent
    H2 or H3 heading before that position.
    Returns the heading text, or 'General' if none found.
    """
    # Find all heading positions in the text
    heading_pattern = re.compile(r'^(#{2,3})\s+(.+)$', re.MULTILINE)
    last_heading = "General"

    for match in heading_pattern.finditer(text):
        if match.start() <= position:
            last_heading = match.group(2).strip()
        else:
            break

    return last_heading


def chunk_document(
    doc: Dict[str, Any],
    chunk_size: int = 600,
    chunk_overlap: int = 80
) -> List[Dict[str, Any]]:
    """
    Split a single document into overlapping text chunks.

    Strategy:
    1. Try to split on paragraph boundaries first (double newlines)
    2. If a paragraph is too long, split mid-text with overlap
    3. Attach metadata: source filename, section heading, chunk index

    Returns list of chunk dicts.
    """
    text = doc["content"]
    filename = doc["filename"]
    chunks = []

    # Split on paragraph boundaries first
    paragraphs = re.split(r'\n\n+', text)

    current_chunk = ""
    chunk_index = 0
    current_pos = 0  # track character position in original text

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed chunk_size, flush current chunk
        if current_chunk and (len(current_chunk) + len(para) + 2 > chunk_size):
            # Save current chunk
            section = _extract_section_for_position(text, current_pos)
            chunks.append({
                "text": current_chunk.strip(),
                "source": filename,
                "section": section,
                "chunk_index": chunk_index
            })
            chunk_index += 1

            # Keep the last `chunk_overlap` characters for context continuity
            overlap_text = current_chunk[-chunk_overlap:].strip() if chunk_overlap > 0 else ""
            current_chunk = (overlap_text + " " + para).strip() if overlap_text else para
        else:
            current_chunk = (current_chunk + "\n\n" + para).strip() if current_chunk else para

        # Track position in original text
        para_pos = text.find(para, current_pos)
        if para_pos != -1:
            current_pos = para_pos

    # Don't forget the last chunk
    if current_chunk.strip():
        section = _extract_section_for_position(text, current_pos)
        chunks.append({
            "text": current_chunk.strip(),
            "source": filename,
            "section": section,
            "chunk_index": chunk_index
        })

    logger.debug(f"{filename}: split into {len(chunks)} chunks")
    return chunks


def ingest_all_documents(
    docs_dir: str,
    chunk_size: int = 600,
    chunk_overlap: int = 80
) -> List[Dict[str, Any]]:
    """
    Full ingestion pipeline: load all docs → chunk them all.
    Returns a flat list of all chunks across all documents.
    """
    documents = load_documents(docs_dir)
    all_chunks = []

    for doc in documents:
        chunks = chunk_document(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        all_chunks.extend(chunks)

    logger.info(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    # Quick test — run this directly to verify ingestion works
    import json
    from config import DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP

    logging.basicConfig(level=logging.INFO)

    chunks = ingest_all_documents(DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP)

    print(f"\n{'='*60}")
    print(f"Total chunks: {len(chunks)}")
    print(f"{'='*60}")

    # Print first 3 chunks as a sanity check
    for chunk in chunks[:3]:
        print(f"\n--- Chunk {chunk['chunk_index']} from {chunk['source']} ---")
        print(f"Section: {chunk['section']}")
        print(f"Text preview: {chunk['text'][:200]}...")
