"""
Overview router — system stats for the dashboard.
"""
from fastapi import APIRouter
from app.services import knowledge_base, vector_store, bm25_store
from app.config import settings

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("")
def get_overview():
    stats = knowledge_base.get_stats()
    registry = knowledge_base.get_registry()

    sources_summary = []
    for v in registry.values():
        sources_summary.append({
            "filename": v["filename"],
            "source_type": v["source_type"],
            "status": v["status"],
            "chunks": v.get("chunks", 0),
            "records": v.get("records", 0),
            "pages": v.get("pages", 0),
            "last_processed": v.get("last_processed"),
        })

    return {
        "app_name": "Enterprise Intelligence Copilot",
        "subtitle": "Unified Enterprise Knowledge & AI Platform",
        "demo_notice": "Demo Environment — Synthetic Enterprise Data",
        "stats": stats,
        "sources": sources_summary,
        "llm_configured": bool(settings.llm_api_key),
        "llm_model": settings.llm_model,
        "llm_provider": settings.llm_provider or "not configured",
    }
