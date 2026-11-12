"""
BM25 keyword search index.
Stores all chunks in memory and provides keyword retrieval.
"""
import logging
import re
from typing import List, Optional

from app.config import settings
from app.models.chunk import Chunk

logger = logging.getLogger(__name__)

# In-memory corpus
_chunks: List[Chunk] = []
_bm25 = None
_tokenized_corpus: List[List[str]] = []


def _tokenize(text: str) -> List[str]:
    """Simple lowercase word tokenizer."""
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def index_chunks(chunks: List[Chunk], reset: bool = False):
    """Add chunks to the BM25 index."""
    global _chunks, _bm25, _tokenized_corpus

    if reset:
        _chunks = []
        _tokenized_corpus = []

    _chunks.extend(chunks)
    new_tokens = [_tokenize(c.content) for c in chunks]
    _tokenized_corpus.extend(new_tokens)

    # Rebuild BM25 index from full corpus
    from rank_bm25 import BM25Okapi
    if _tokenized_corpus:
        _bm25 = BM25Okapi(_tokenized_corpus)
        logger.info(f"BM25 index built with {len(_chunks)} documents")
    else:
        _bm25 = None


def keyword_search(query: str, top_k: Optional[int] = None) -> List[dict]:
    """Search BM25 index for keyword-matching chunks."""
    if _bm25 is None or not _chunks:
        return []

    top_k = top_k or settings.bm25_top_k
    query_tokens = _tokenize(query)
    scores = _bm25.get_scores(query_tokens)

    # Get indices of top_k highest scores
    import numpy as np
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            chunk = _chunks[idx]
            results.append({
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.source_file,
                "source_type": chunk.source_type,
                "content": chunk.content,
                "metadata": chunk.metadata,
                "score": float(scores[idx]),
            })

    return results


def corpus_size() -> int:
    return len(_chunks)


def is_ready() -> bool:
    return _bm25 is not None and len(_chunks) > 0
