"""
Knowledge Sources router — list, upload, trigger processing.
"""
import shutil
import asyncio
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.config import settings
from app.services import knowledge_base

router = APIRouter(prefix="/api/sources", tags=["sources"])


class SourceInfo(BaseModel):
    filename: str
    source_type: str
    status: str
    chunks: int
    records: int
    pages: int
    last_processed: str | None
    error: str | None
    logs: List[str]


@router.get("", response_model=List[SourceInfo])
def list_sources():
    registry = knowledge_base.get_registry()
    return [
        SourceInfo(
            filename=v["filename"],
            source_type=v["source_type"],
            status=v["status"],
            chunks=v.get("chunks", 0),
            records=v.get("records", 0),
            pages=v.get("pages", 0),
            last_processed=v.get("last_processed"),
            error=v.get("error"),
            logs=v.get("logs", []),
        )
        for v in registry.values()
    ]


@router.get("/{filename}", response_model=SourceInfo)
def get_source(filename: str):
    src = knowledge_base.get_source(filename.lower().replace(" ", "_"))
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceInfo(
        filename=src["filename"],
        source_type=src["source_type"],
        status=src["status"],
        chunks=src.get("chunks", 0),
        records=src.get("records", 0),
        pages=src.get("pages", 0),
        last_processed=src.get("last_processed"),
        error=src.get("error"),
        logs=src.get("logs", []),
    )


@router.post("/{filename}/process")
async def process_source(filename: str, background_tasks: BackgroundTasks):
    """Trigger (re)processing of an existing source."""
    src = knowledge_base.get_source(filename.lower().replace(" ", "_"))
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")

    background_tasks.add_task(knowledge_base.process_source, filename)
    return {"message": f"Processing started for {filename}", "status": "processing"}


@router.post("/upload")
async def upload_source(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a new CSV/XLSX/PDF file and queue it for processing."""
    allowed_extensions = {".csv", ".xlsx", ".xls", ".pdf"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Allowed: {allowed_extensions}",
        )

    dest = settings.upload_dir / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    source_type = "pdf" if suffix == ".pdf" else ("xlsx" if suffix in (".xlsx", ".xls") else "csv")
    knowledge_base.register_source(file.filename, source_type, dest)
    background_tasks.add_task(knowledge_base.process_source, file.filename)

    return {
        "message": f"Uploaded {file.filename}, processing started",
        "filename": file.filename,
        "status": "processing",
    }


@router.post("/process-all")
async def process_all(background_tasks: BackgroundTasks):
    """Re-process all registered sources."""
    background_tasks.add_task(knowledge_base.process_all_defaults)
    return {"message": "Processing all default sources started"}
