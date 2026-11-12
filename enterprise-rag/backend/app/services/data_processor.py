"""
Data ingestion, cleaning, OCR, chunking, and metadata extraction.
Processes CSV, XLSX, and PDF files into Chunk objects.
"""
import re
import uuid
import logging
from pathlib import Path
from typing import List, Generator, Tuple
import pandas as pd

from app.config import settings
from app.models.chunk import Chunk

logger = logging.getLogger(__name__)


# ─── chunking helper ─────────────────────────────────────────────────────────

def _split_text(text: str, size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping word-level chunks."""
    size = size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break
        start += size - overlap
    return chunks


def _clean_text(text: str) -> str:
    """Normalise whitespace and remove control characters."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─── CSV processor ───────────────────────────────────────────────────────────

def process_csv(path: Path) -> Tuple[List[Chunk], dict]:
    """
    Load CSV, clean, deduplicate, and chunk each row as a text block.
    Returns (chunks, stats).
    """
    logger.info(f"Processing CSV: {path.name}")
    df = pd.read_csv(path, dtype=str)

    # --- cleaning ---
    original_len = len(df)
    df.drop_duplicates(inplace=True)
    df.fillna("N/A", inplace=True)
    # strip whitespace in string columns
    for col in df.columns:
        df[col] = df[col].str.strip()

    stats = {
        "source_file": path.name,
        "source_type": "csv",
        "total_rows": len(df),
        "duplicates_removed": original_len - len(df),
        "columns": list(df.columns),
    }

    chunks: List[Chunk] = []
    for _, row in df.iterrows():
        # Build a readable text block from the row
        lines = [f"{k}: {v}" for k, v in row.items() if v != "N/A"]
        text = _clean_text("\n".join(lines))
        if not text:
            continue

        # Use first column as primary key if available
        metadata = row.to_dict()
        metadata["source_file"] = path.name
        metadata["source_type"] = "csv"

        for sub_chunk in _split_text(text):
            chunks.append(Chunk(
                chunk_id=str(uuid.uuid4()),
                source_file=path.name,
                source_type="csv",
                content=sub_chunk,
                metadata=metadata,
            ))

    stats["chunks_produced"] = len(chunks)
    logger.info(f"  → {len(chunks)} chunks from {len(df)} rows")
    return chunks, stats


# ─── XLSX processor ──────────────────────────────────────────────────────────

def process_xlsx(path: Path) -> Tuple[List[Chunk], dict]:
    """Load XLSX, clean, and chunk."""
    logger.info(f"Processing XLSX: {path.name}")
    xl = pd.ExcelFile(path)
    all_chunks: List[Chunk] = []
    sheet_stats = []

    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name, dtype=str)
        original_len = len(df)
        df.drop_duplicates(inplace=True)
        df.fillna("N/A", inplace=True)
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()

        sheet_stats.append({
            "sheet": sheet_name,
            "rows": len(df),
            "duplicates_removed": original_len - len(df),
        })

        for row_idx, (_, row) in enumerate(df.iterrows()):
            lines = [f"{k}: {v}" for k, v in row.items() if v not in ("N/A", "nan")]
            text = _clean_text("\n".join(lines))
            if not text:
                continue

            metadata = row.to_dict()
            metadata["source_file"] = path.name
            metadata["source_type"] = "xlsx"
            metadata["sheet"] = sheet_name
            metadata["row_index"] = row_idx + 2  # 1-based with header = row 1

            for sub_chunk in _split_text(text):
                all_chunks.append(Chunk(
                    chunk_id=str(uuid.uuid4()),
                    source_file=path.name,
                    source_type="xlsx",
                    content=sub_chunk,
                    metadata=metadata,
                ))

    stats = {
        "source_file": path.name,
        "source_type": "xlsx",
        "sheets": sheet_stats,
        "total_chunks": len(all_chunks),
    }
    logger.info(f"  → {len(all_chunks)} chunks from XLSX")
    return all_chunks, stats


# ─── PDF processor ───────────────────────────────────────────────────────────

def process_pdf(path: Path) -> Tuple[List[Chunk], dict]:
    """
    Extract text from PDF using PyMuPDF.
    Falls back to Tesseract OCR for image-only pages if available.
    """
    logger.info(f"Processing PDF: {path.name}")
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF not installed")
        return [], {"error": "PyMuPDF not installed"}

    doc = fitz.open(str(path))
    all_chunks: List[Chunk] = []
    page_stats = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")

        # OCR fallback for image-heavy pages
        if len(text.strip()) < 50:
            text = _ocr_page(page, page_num) or text

        text = _clean_text(text)
        if not text:
            page_stats.append({"page": page_num, "chars": 0, "chunks": 0})
            continue

        page_meta = {
            "source_file": path.name,
            "source_type": "pdf",
            "page": page_num,
            "total_pages": len(doc),
        }

        page_chunks = _split_text(text)
        for sub_chunk in page_chunks:
            all_chunks.append(Chunk(
                chunk_id=str(uuid.uuid4()),
                source_file=path.name,
                source_type="pdf",
                content=sub_chunk,
                metadata={**page_meta},
            ))

        page_stats.append({"page": page_num, "chars": len(text), "chunks": len(page_chunks)})

    doc.close()
    stats = {
        "source_file": path.name,
        "source_type": "pdf",
        "total_pages": len(doc) if not doc.is_closed else page_num,
        "pages": page_stats,
        "total_chunks": len(all_chunks),
    }
    logger.info(f"  → {len(all_chunks)} chunks from PDF ({page_num} pages)")
    return all_chunks, stats


def _ocr_page(page, page_num: int) -> str:
    """Attempt Tesseract OCR on a PDF page rendered as image."""
    try:
        import pytesseract
        from PIL import Image
        import io

        mat = page.get_pixmap(dpi=200)
        img_bytes = mat.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img)
        logger.info(f"    OCR applied to page {page_num}")
        return text
    except Exception as e:
        logger.debug(f"    OCR unavailable for page {page_num}: {e}")
        return ""


# ─── Unified dispatcher ───────────────────────────────────────────────────────

def process_file(path: Path) -> Tuple[List[Chunk], dict]:
    """Route a file to the correct processor based on extension."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return process_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return process_xlsx(path)
    elif suffix == ".pdf":
        return process_pdf(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
