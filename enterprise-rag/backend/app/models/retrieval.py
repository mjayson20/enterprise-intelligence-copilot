from pydantic import BaseModel
from typing import List, Optional


class RetrievedChunk(BaseModel):
    chunk_id: str
    source_file: str
    source_type: str
    content: str
    metadata: dict
    score: float
    rank: int


class RetrievalResult(BaseModel):
    semantic_results: List[RetrievedChunk]
    bm25_results: List[RetrievedChunk]
    fused_results: List[RetrievedChunk]
    query: str


class Citation(BaseModel):
    source_file: str
    source_type: str
    metadata: dict
    snippet: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    retrieval: RetrievalResult
    model_used: str
