"""
Query router — AI Copilot and Retrieval Explorer endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import hybrid_retrieval, bm25_store, vector_store, llm_service
from app.models.retrieval import QueryResponse

router = APIRouter(prefix="/api/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str


class RetrievalOnlyRequest(BaseModel):
    query: str


@router.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    """
    Full RAG pipeline:
    1. Hybrid retrieval (semantic + BM25 + RRF)
    2. LLM grounded answer with citations
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not bm25_store.is_ready() and not vector_store.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Knowledge base not yet indexed. Please process sources first.",
        )

    # 1. Hybrid retrieval
    retrieval_result = hybrid_retrieval.hybrid_search(question)

    # 2. LLM answer
    context_chunks = retrieval_result.fused_results[:6]
    answer, citations, model_used = llm_service.generate_answer(question, context_chunks)

    return QueryResponse(
        question=question,
        answer=answer,
        citations=citations,
        retrieval=retrieval_result,
        model_used=model_used,
    )


@router.post("/retrieve")
async def retrieve_only(request: RetrievalOnlyRequest):
    """
    Retrieval Explorer endpoint — returns semantic, BM25, and fused results
    without calling the LLM.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = hybrid_retrieval.hybrid_search(query)
    return result
