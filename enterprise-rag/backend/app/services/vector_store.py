"""
Vector store service using Qdrant (in-memory) + Sentence Transformers.
Handles embedding generation and semantic search.
"""
import logging
import uuid
from typing import List, Optional

from app.config import settings
from app.models.chunk import Chunk

logger = logging.getLogger(__name__)

# Lazy globals — initialised on first use
_encoder = None
_qdrant_client = None
_collection_ready = False


def _get_encoder():
    """
    Try SentenceTransformer first; fall back to a sklearn TF-IDF vectorizer
    (fixed 384-dim projection) if torch/transformers are not installed.
    """
    global _encoder
    if _encoder is None:
        try:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            from sentence_transformers import SentenceTransformer
            _encoder = SentenceTransformer(settings.embedding_model)
            logger.info("Sentence-Transformers encoder loaded.")
        except Exception as e:
            logger.warning(f"SentenceTransformer unavailable ({e}). Using TF-IDF fallback.")
            _encoder = _TfidfEncoder()
    return _encoder


class _TfidfEncoder:
    """
    Lightweight fallback encoder using TF-IDF + random projection to 384 dims.
    Produces deterministic (but lower-quality) dense vectors.
    """
    def __init__(self):
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._vec = TfidfVectorizer(max_features=4096, sublinear_tf=True)
        self._fitted = False
        self._corpus: list[str] = []
        rng = np.random.default_rng(42)
        self._proj = rng.standard_normal((4096, settings.embedding_dim)).astype("float32")
        self._proj /= np.linalg.norm(self._proj, axis=1, keepdims=True)

    def _fit_if_needed(self, texts: list[str]):
        import numpy as np
        if not self._fitted:
            all_texts = self._corpus + texts
            self._vec.fit(all_texts)
            self._fitted = True
        self._corpus.extend(texts)

    def encode(self, texts, batch_size=64, show_progress_bar=False):
        import numpy as np
        if isinstance(texts, str):
            texts = [texts]
        self._fit_if_needed(texts)
        tfidf = self._vec.transform(texts).toarray().astype("float32")
        vecs = tfidf @ self._proj[:tfidf.shape[1]]
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return vecs / norms


def _get_client():
    global _qdrant_client
    if _qdrant_client is None:
        from qdrant_client import QdrantClient
        if settings.qdrant_use_memory:
            logger.info("Starting Qdrant in-memory client")
            _qdrant_client = QdrantClient(":memory:")
        else:
            logger.info(f"Connecting to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")
            _qdrant_client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
    return _qdrant_client


def _ensure_collection(recreate: bool = False):
    global _collection_ready
    from qdrant_client.models import Distance, VectorParams

    client = _get_client()
    col = settings.qdrant_collection

    existing = [c.name for c in client.get_collections().collections]
    if col in existing and recreate:
        client.delete_collection(col)
        existing = []

    if col not in existing:
        client.create_collection(
            collection_name=col,
            vectors_config=VectorParams(
                size=settings.embedding_dim,
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"Created Qdrant collection: {col}")

    _collection_ready = True


def embed_and_index(chunks: List[Chunk], recreate: bool = False) -> int:
    """
    Generate embeddings for chunks and upsert into Qdrant.
    Returns number of vectors stored.
    """
    if not chunks:
        return 0

    _ensure_collection(recreate=recreate)
    encoder = _get_encoder()
    client = _get_client()

    from qdrant_client.models import PointStruct

    texts = [c.content for c in chunks]
    logger.info(f"Generating embeddings for {len(texts)} chunks …")
    embeddings = encoder.encode(texts, batch_size=64, show_progress_bar=False)

    points = []
    for chunk, vector in zip(chunks, embeddings):
        # Qdrant needs a numeric or UUID id
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
        points.append(PointStruct(
            id=point_id,
            vector=vector.tolist(),
            payload={
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.source_file,
                "source_type": chunk.source_type,
                "content": chunk.content,
                "metadata": chunk.metadata,
            },
        ))

    # Upsert in batches
    batch_size = 256
    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name=settings.qdrant_collection,
            points=points[i:i + batch_size],
        )

    logger.info(f"Indexed {len(points)} vectors into Qdrant")
    global _indexed_count
    _indexed_count += len(points)
    return len(points)


def semantic_search(query: str, top_k: Optional[int] = None) -> List[dict]:
    """
    Search Qdrant for semantically similar chunks.
    Returns list of dicts with payload + score.
    """
    top_k = top_k or settings.semantic_top_k
    _ensure_collection()
    encoder = _get_encoder()
    client = _get_client()

    query_vector = encoder.encode(query).tolist()
    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "chunk_id": r.payload["chunk_id"],
            "source_file": r.payload["source_file"],
            "source_type": r.payload["source_type"],
            "content": r.payload["content"],
            "metadata": r.payload["metadata"],
            "score": r.score,
        }
        for r in results
    ]


_indexed_count = 0  # track manually since in-memory Qdrant may not report count


def collection_count() -> int:
    """Return number of vectors indexed (tracked manually for in-memory mode)."""
    global _indexed_count
    try:
        _ensure_collection()
        info = _get_client().get_collection(settings.qdrant_collection)
        reported = info.vectors_count or 0
        return reported if reported > 0 else _indexed_count
    except Exception:
        return _indexed_count


def is_ready() -> bool:
    try:
        _ensure_collection()
        return True
    except Exception:
        return False
