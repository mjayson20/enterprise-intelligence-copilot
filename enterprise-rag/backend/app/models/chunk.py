from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Chunk:
    """A single indexed knowledge chunk."""
    chunk_id: str
    source_file: str          # e.g. "crm_customers.csv"
    source_type: str          # csv | xlsx | pdf
    content: str              # raw text of the chunk
    metadata: dict = field(default_factory=dict)
    embedding: Optional[list] = None  # filled during indexing
