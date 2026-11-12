"""
Knowledge Base orchestrator.
Manages the full pipeline: ingest → process → embed → index.
Maintains processing state for all sources.
"""
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.config import settings
from app.services import data_processor, vector_store, bm25_store
from app.models.chunk import Chunk

logger = logging.getLogger(__name__)

# ─── Processing state registry ────────────────────────────────────────────────

class SourceStatus:
    PENDING   = "pending"
    PROCESSING = "processing"
    INDEXED   = "indexed"
    ERROR     = "error"


_source_registry: Dict[str, dict] = {}
_all_chunks: List[Chunk] = []


def _make_source_key(filename: str) -> str:
    return filename.lower().replace(" ", "_")


def get_registry() -> Dict[str, dict]:
    return _source_registry


def get_source(key: str) -> Optional[dict]:
    return _source_registry.get(key)


def register_source(filename: str, source_type: str, path: Path):
    key = _make_source_key(filename)
    _source_registry[key] = {
        "filename": filename,
        "source_type": source_type,
        "path": str(path),
        "status": SourceStatus.PENDING,
        "chunks": 0,
        "records": 0,
        "pages": 0,
        "last_processed": None,
        "error": None,
        "stats": {},
        "logs": [],
    }
    return key


def _log(key: str, msg: str):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    _source_registry[key]["logs"].append(entry)
    logger.info(f"[{key}] {msg}")


async def process_source(filename: str, path: Optional[Path] = None) -> dict:
    """
    Run the full pipeline for a single source file (async wrapper).
    """
    key = _make_source_key(filename)

    if key not in _source_registry:
        # Auto-register if not already present
        path = path or settings.data_dir / filename
        ext = Path(filename).suffix.lower().lstrip(".")
        source_type = "pdf" if ext == "pdf" else ("xlsx" if ext in ("xlsx", "xls") else "csv")
        register_source(filename, source_type, path)

    src = _source_registry[key]
    src["status"] = SourceStatus.PROCESSING
    src["logs"] = []
    src["error"] = None

    file_path = Path(src["path"])

    try:
        # ── Step 1: Ingestion ──────────────────────────────────────────
        _log(key, f"Step 1/5 — Ingestion: reading {filename}")
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # ── Step 2: Parsing + Cleaning ─────────────────────────────────
        _log(key, "Step 2/5 — Parsing & cleaning …")
        loop = asyncio.get_event_loop()
        chunks, stats = await loop.run_in_executor(
            None, data_processor.process_file, file_path
        )
        src["stats"] = stats
        src["chunks"] = len(chunks)

        # Surface record / page count
        if src["source_type"] == "csv":
            src["records"] = stats.get("total_rows", 0)
        elif src["source_type"] == "xlsx":
            total = sum(s.get("rows", 0) for s in stats.get("sheets", []))
            src["records"] = total
        elif src["source_type"] == "pdf":
            src["pages"] = stats.get("total_pages", 0)

        _log(key, f"  ✓ Parsed: {src['records'] or src['pages']} records/pages → {len(chunks)} chunks")

        # ── Step 3: Metadata ───────────────────────────────────────────
        _log(key, "Step 3/5 — Metadata extraction complete (embedded in chunks)")

        # ── Step 4: Embeddings + Vector Index ──────────────────────────
        _log(key, "Step 4/5 — Generating embeddings & indexing in Qdrant …")
        count = await loop.run_in_executor(
            None, lambda: vector_store.embed_and_index(chunks)
        )
        _log(key, f"  ✓ {count} vectors stored in Qdrant")

        # ── Step 5: BM25 Index ─────────────────────────────────────────
        _log(key, "Step 5/5 — Building BM25 keyword index …")
        bm25_store.index_chunks(chunks)
        _log(key, f"  ✓ BM25 index updated ({bm25_store.corpus_size()} total docs)")

        # Register chunks globally for stats
        _all_chunks.extend(chunks)

        src["status"] = SourceStatus.INDEXED
        src["last_processed"] = datetime.utcnow().isoformat()
        _log(key, "✓ Source fully indexed")

    except Exception as e:
        src["status"] = SourceStatus.ERROR
        src["error"] = str(e)
        _log(key, f"✗ Error: {e}")
        logger.exception(f"Processing failed for {filename}")

    return src


async def process_all_defaults():
    """Process all default data files in the data directory."""
    data_dir = settings.data_dir
    docs_dir = data_dir / "documents"

    default_files = [
        (data_dir / "crm_customers.csv", "csv"),
        (data_dir / "sales_transactions.xlsx", "xlsx"),
        (data_dir / "support_tickets.csv", "csv"),
        (docs_dir / "customer_policy.pdf", "pdf"),
        (docs_dir / "support_policy.pdf", "pdf"),
        (docs_dir / "product_catalog.pdf", "pdf"),
        (docs_dir / "invoice_samples.pdf", "pdf"),
    ]

    for path, stype in default_files:
        if path.exists():
            key = register_source(path.name, stype, path)
        else:
            logger.warning(f"Default file not found: {path}")

    # Process sequentially to avoid memory spikes
    for path, _ in default_files:
        if path.exists():
            await process_source(path.name)


def total_chunks() -> int:
    return len(_all_chunks)


def get_stats() -> dict:
    indexed = [s for s in _source_registry.values() if s["status"] == SourceStatus.INDEXED]
    return {
        "total_sources": len(_source_registry),
        "indexed_sources": len(indexed),
        "total_chunks": bm25_store.corpus_size(),
        "vector_count": vector_store.collection_count(),
        "bm25_docs": bm25_store.corpus_size(),
        "vector_db_ready": vector_store.is_ready(),
        "bm25_ready": bm25_store.is_ready(),
    }
