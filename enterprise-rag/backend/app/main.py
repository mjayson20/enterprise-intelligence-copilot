"""
Enterprise Intelligence Copilot — FastAPI backend
Demo Environment — Synthetic Enterprise Data
"""
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import overview, sources, query
from app.services import knowledge_base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup: register default sources. Processing is triggered manually or via API."""
    logger.info("Enterprise Intelligence Copilot starting up …")
    logger.info("Demo Environment — Synthetic Enterprise Data")

    # Register default sources (don't auto-process — let user trigger from UI)
    from pathlib import Path
    from app.config import settings
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

    # Register and auto-process default sources on startup
    for path, stype in default_files:
        if path.exists():
            knowledge_base.register_source(path.name, stype, path)
            logger.info(f"  Registered: {path.name}")
        else:
            logger.warning(f"  Not found (run data generator first): {path.name}")

    # Auto-process all sources on startup for convenience
    # (comment this out if you want to trigger processing manually from the UI)
    import asyncio
    asyncio.create_task(knowledge_base.process_all_defaults())

    yield
    logger.info("Shutting down …")


app = FastAPI(
    title="Enterprise Intelligence Copilot",
    description="Unified Enterprise Knowledge & AI Platform — Demo Environment",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow local frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://localhost:5174",
        "http://localhost:3000", "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router)
app.include_router(sources.router)
app.include_router(query.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Enterprise Intelligence Copilot"}
