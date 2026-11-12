"""
Hybrid Retrieval: Semantic (Qdrant) + Keyword (BM25) → RRF Fusion.

Reciprocal Rank Fusion formula:
    RRF(d) = Σ 1 / (k + rank(d))
where k is a smoothing constant (default 60).
"""
import logging
from typing import List, Dict, Tuple, Optional

from app.config import settings
from app.models.retrieval import RetrievedChunk, RetrievalResult
from app.services import vector_store, bm25_store

logger = logging.getLogger(__name__)


def _rrf_score(rank: int, k: int = None) -> float:
    k = k or settings.rrf_k
    return 1.0 / (k + rank)


def reciprocal_rank_fusion(
    semantic_hits: List[dict],
    bm25_hits: List[dict],
    k: int = None,
    top_k: int = None,
) -> List[dict]:
    """
    Combine two ranked lists using Reciprocal Rank Fusion.
    Returns merged, deduplicated list sorted by RRF score descending.
    """
    k = k or settings.rrf_k
    top_k = top_k or settings.final_top_k

    # Map chunk_id → accumulated RRF score and payload
    fused: Dict[str, dict] = {}

    for rank, hit in enumerate(semantic_hits, start=1):
        cid = hit["chunk_id"]
        if cid not in fused:
            fused[cid] = {**hit, "rrf_score": 0.0, "in_semantic": True, "in_bm25": False}
        fused[cid]["rrf_score"] += _rrf_score(rank, k)
        fused[cid]["in_semantic"] = True

    for rank, hit in enumerate(bm25_hits, start=1):
        cid = hit["chunk_id"]
        if cid not in fused:
            fused[cid] = {**hit, "rrf_score": 0.0, "in_semantic": False, "in_bm25": True}
        fused[cid]["rrf_score"] += _rrf_score(rank, k)
        fused[cid]["in_bm25"] = True

    # Sort by RRF score, take top_k
    ranked = sorted(fused.values(), key=lambda x: x["rrf_score"], reverse=True)[:top_k]
    return ranked


def hybrid_search(query: str) -> RetrievalResult:
    """
    Run semantic search, BM25 search, fuse with RRF, return structured result.
    """
    logger.info(f"Hybrid search for: {query!r}")

    # 1. Semantic retrieval
    sem_hits = vector_store.semantic_search(query, top_k=settings.semantic_top_k)
    # 2. BM25 keyword retrieval
    kw_hits = bm25_store.keyword_search(query, top_k=settings.bm25_top_k)
    # 3. RRF fusion
    fused = reciprocal_rank_fusion(sem_hits, kw_hits)

    def _to_chunk(hits: List[dict], score_key: str = "score") -> List[RetrievedChunk]:
        out = []
        for rank, h in enumerate(hits, start=1):
            out.append(RetrievedChunk(
                chunk_id=h["chunk_id"],
                source_file=h["source_file"],
                source_type=h["source_type"],
                content=h["content"],
                metadata=h["metadata"],
                score=round(h.get(score_key, 0.0), 4),
                rank=rank,
            ))
        return out

    fused_chunks = []
    for rank, h in enumerate(fused, start=1):
        fused_chunks.append(RetrievedChunk(
            chunk_id=h["chunk_id"],
            source_file=h["source_file"],
            source_type=h["source_type"],
            content=h["content"],
            metadata=h["metadata"],
            score=round(h["rrf_score"], 6),
            rank=rank,
        ))

    return RetrievalResult(
        query=query,
        semantic_results=_to_chunk(sem_hits, "score"),
        bm25_results=_to_chunk(kw_hits, "score"),
        fused_results=fused_chunks,
    )
