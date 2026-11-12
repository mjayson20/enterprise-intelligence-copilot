from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # LLM — Groq (free, OpenAI-compatible API)
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    # Keep old names as aliases so a stale .env doesn't crash
    openai_api_key: str = ""
    openai_model: str = ""

    # Qdrant (in-memory by default for MVP — no Docker required)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_use_memory: bool = True          # True = in-process, no server needed
    qdrant_collection: str = "enterprise_rag"

    # Embedding model (runs locally)
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Paths
    data_dir: Path = Path(__file__).parent.parent.parent / "data"
    upload_dir: Path = Path(__file__).parent.parent / "uploads"

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Retrieval
    semantic_top_k: int = 10
    bm25_top_k: int = 10
    final_top_k: int = 6
    rrf_k: int = 60          # RRF constant

    class Config:
        env_file = ".env"
        extra = "ignore"

    # ── LLM resolution helpers ──────────────────────────────────────────
    @property
    def llm_api_key(self) -> str:
        """Use Groq key, fall back to OpenAI key if only that is set."""
        return self.groq_api_key or self.openai_api_key

    @property
    def llm_model(self) -> str:
        """Use Groq model, fall back to OpenAI model if only that is set."""
        return self.groq_model or self.openai_model or "openai/gpt-oss-120b"

    @property
    def llm_provider(self) -> str:
        """Which provider are we talking to?"""
        return "groq" if self.groq_api_key else ("openai" if self.openai_api_key else "")

    @property
    def llm_base_url(self) -> str:
        return "https://api.groq.com/openai/v1" if self.llm_provider == "groq" else None

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_api_key)


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
