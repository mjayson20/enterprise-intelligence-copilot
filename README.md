# Enterprise Intelligence Copilot
### Unified Enterprise Knowledge & AI Platform

> **Demo Environment — Synthetic Enterprise Data**
> All data in this project is entirely fictional and belongs to a fictitious company called "Acme Enterprise".

---

## Project Purpose

A university Phase-1 prototype demonstrating **Primary Objective 01**:

1. **Data Unification** — CRM, Excel/CSV, and PDF business documents merged into one searchable knowledge base
2. **Data Processing** — Real pipeline: ingestion → cleaning → OCR → metadata → chunking → embeddings
3. **Hybrid RAG** — Semantic search (Qdrant) + BM25 keyword search → Reciprocal Rank Fusion → LLM → Grounded answer with citations

---

## Synthetic Dataset

All data is fictional. The company "Acme Enterprise" and all customers, transactions, and documents are made up for demonstration purposes.

```
data/
├── crm_customers.csv           # 20 synthetic customers
├── sales_transactions.xlsx     # 200 synthetic transactions
├── support_tickets.csv         # 150 synthetic support tickets
└── documents/
    ├── customer_policy.pdf     # Customer classification & policy
    ├── support_policy.pdf      # SLA definitions (P1–P4)
    ├── product_catalog.pdf     # 9 product descriptions & pricing
    └── invoice_samples.pdf     # 4 sample invoices
```

### Dataset Schemas

**crm_customers.csv**
| Field | Description |
|-------|-------------|
| customer_id | CUST-001 to CUST-020 |
| customer_name | Fictional company name |
| industry | e.g. Technology, Finance |
| region | e.g. North America, Europe |
| account_manager | Assigned AM name |
| annual_revenue | Integer (500k–50M) |
| employee_count | Integer (50–10,000) |
| customer_since | Date (YYYY-MM-DD) |
| account_status | Active / At Risk / Churned |

**sales_transactions.xlsx** (Sheet: Sales)
| Field | Description |
|-------|-------------|
| transaction_id | TXN-0001 to TXN-0200 |
| customer_id | FK to CRM |
| product | Product name |
| sales_date | Date |
| quantity | Integer |
| unit_price | Integer |
| sales_amount | quantity × unit_price |
| region | Region |
| sales_rep | Rep name |
| status | Closed Won / Closed Lost / Pending |

**support_tickets.csv**
| Field | Description |
|-------|-------------|
| ticket_id | TKT-0001 to TKT-0150 |
| customer_id | FK to CRM |
| issue_type | e.g. Technical Support, Billing Issue |
| priority | P1 / P2 / P3 / P4 |
| product | Product name |
| created_date | Date |
| status | Open / In Progress / Resolved |
| resolution_time_hours | Float (blank if unresolved) |
| description | Text description |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Data Processing | Pandas, OpenPyXL, PyMuPDF |
| OCR | Tesseract (optional fallback) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB | Qdrant (in-memory, no server needed) |
| Keyword Search | BM25 (rank-bm25) |
| LLM | Groq API (free, OpenAI-compatible) |

---

## Architecture

```
CRM (CSV) + Sales (XLSX) + PDFs
         │
         ▼
  ┌─────────────────┐
  │  Data Processor  │  ← Pandas, PyMuPDF, OCR
  │  - Load & clean  │
  │  - Chunk (512w)  │
  │  - Extract meta  │
  └────────┬────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
  Qdrant        BM25 Index
  (vectors)     (keyword)
     │            │
     └─────┬──────┘
           ▼
   RRF Fusion (k=60)
           │
           ▼
     Top-K Context
           │
           ▼
      OpenAI LLM
           │
           ▼
  Grounded Answer + Citations
```

## How Hybrid RAG Works

1. **Semantic Search**: Query is encoded to a 384-dim vector using `all-MiniLM-L6-v2`. Qdrant finds the top-10 most similar chunks by cosine similarity.

2. **BM25 Keyword Search**: Query is tokenized. BM25 Okapi scores all 384 corpus documents and returns top-10 keyword matches.

3. **RRF Fusion**: Results from both lists are merged using Reciprocal Rank Fusion:
   ```
   RRF(d) = 1/(60 + rank_semantic) + 1/(60 + rank_bm25)
   ```
   This rewards documents that appear in both lists.

4. **LLM Grounded Answer**: The top-6 fused chunks are sent to the LLM with a strict prompt: "Answer ONLY from the provided context. Cite sources."

5. **Citations**: Every answer includes source references (filename, page, row).

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Clone / open the project

```bash
cd enterprise-rag
```

### 2. Generate synthetic data

```bash
cd data
pip install pandas openpyxl PyMuPDF
python generate_data.py
cd ..
```

### 3. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

> Note: `sentence-transformers` will download the `all-MiniLM-L6-v2` model (~90MB) on first run.

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 5. Install frontend dependencies

```bash
cd ../frontend
npm install
```

---

## Running the Application

### Start backend (Terminal 1)
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Start frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

### Process data sources

On the **Knowledge Sources** page, click **Process All** to ingest all 7 data sources.

Or trigger via API:
```bash
curl -X POST http://localhost:8000/api/sources/process-all
```

---

## Groq API Key (free)

Groq provides free LLM inference using an OpenAI-compatible API.

1. Get a free key at **https://console.groq.com/keys**
2. Add to `backend/.env`:
   ```
   GROQ_API_KEY=gsk_your-key-here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```
3. Restart the backend.

**Available models** (all free tier):
- `openai/gpt-oss-120b` — OpenAI's open-weight 120B model (default)
- `openai/gpt-oss-20b` — faster, lighter 20B variant
- `qwen/qwen3.8-27b` — Qwen 27B

Without a key, the system still performs full hybrid retrieval and shows retrieved context — only the LLM-generated answer is skipped.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | (empty) | Your free Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model to use |
| `QDRANT_USE_MEMORY` | `true` | Use in-memory Qdrant (no server needed) |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence Transformers model |
| `CHUNK_SIZE` | `512` | Words per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |

---

## Example Test Questions

1. **"Which customers generated the highest sales?"**
   — Retrieves from `sales_transactions.xlsx`, aggregates by customer_id

2. **"What is the support policy for P1 tickets?"**
   — Retrieves from `support_policy.pdf` pages 1-2 with exact SLA times

3. **"Which high-value customers have unresolved high-priority support tickets?"**
   — Cross-source: joins `crm_customers.csv` revenue with `support_tickets.csv` status

4. **"Summarize the information available about customer CUST-001."**
   — Retrieves from CRM, sales, tickets, and invoices for CUST-001

5. **"What products generate the most revenue?"**
   — Aggregates `sales_transactions.xlsx` by product + cross-references `product_catalog.pdf`

---

## Primary Objective 01 — Where Each Requirement Is Implemented

### Data Unification (CRM + Excel + PDF → Unified Knowledge Base)
- `backend/app/services/data_processor.py` — `process_csv()`, `process_xlsx()`, `process_pdf()`
- `backend/app/services/knowledge_base.py` — `process_all_defaults()` orchestrates all sources
- Common `customer_id` field links CSV, XLSX, and PDF invoice data
- All chunks stored in unified Qdrant collection + BM25 corpus

### Data Processing (Raw Data → Cleaning → OCR → Metadata → Chunking → Embeddings)
- Ingestion: `process_file()` dispatcher in `data_processor.py`
- Cleaning: deduplication, null handling, whitespace normalisation (Pandas)
- OCR: `_ocr_page()` uses Tesseract via `pytesseract` as fallback for image-only PDF pages
- Metadata: every chunk carries `source_file`, `source_type`, `page`/`row_index`
- Chunking: `_split_text()` — sliding window, 512 words, 64-word overlap
- Embeddings: `vector_store.embed_and_index()` using `all-MiniLM-L6-v2`
- Indexing: Qdrant (vector) + BM25 (keyword) both updated per source

### Hybrid RAG (Query → Semantic + BM25 → RRF → LLM → Grounded Answer + Citations)
- Semantic: `vector_store.semantic_search()` — Qdrant cosine similarity
- Keyword: `bm25_store.keyword_search()` — Okapi BM25
- RRF Fusion: `hybrid_retrieval.reciprocal_rank_fusion()` — pure RRF, k=60
- LLM: `llm_service.generate_answer()` — system prompt enforces grounded answers only
- Citations: `_extract_citations()` builds source references from chunk metadata
- Demonstrated live in **Retrieval Explorer** page (side-by-side semantic / BM25 / fused)

---

## Project Structure

```
enterprise-rag/
├── README.md
├── data/
│   ├── generate_data.py         # Synthetic data generator
│   ├── crm_customers.csv
│   ├── sales_transactions.xlsx
│   ├── support_tickets.csv
│   └── documents/
│       ├── customer_policy.pdf
│       ├── support_policy.pdf
│       ├── product_catalog.pdf
│       └── invoice_samples.pdf
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py              # FastAPI app, startup
│       ├── config.py            # Settings from .env
│       ├── models/
│       │   ├── chunk.py         # Chunk dataclass
│       │   └── retrieval.py     # Pydantic response models
│       ├── routers/
│       │   ├── overview.py      # GET /api/overview
│       │   ├── sources.py       # Sources CRUD + processing
│       │   └── query.py         # /api/query/ask + /retrieve
│       └── services/
│           ├── data_processor.py    # CSV/XLSX/PDF → Chunks
│           ├── vector_store.py      # Qdrant + embeddings
│           ├── bm25_store.py        # BM25 index
│           ├── hybrid_retrieval.py  # RRF fusion
│           ├── llm_service.py       # OpenAI grounded answers
│           └── knowledge_base.py    # Orchestration + state
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx
        ├── lib/api.ts           # Backend API client
        ├── components/
        │   ├── Sidebar.tsx
        │   ├── StatusBadge.tsx
        │   └── MetricCard.tsx
        └── pages/
            ├── Overview.tsx          # Dashboard
            ├── KnowledgeSources.tsx  # Source management
            ├── DataProcessing.tsx    # Pipeline visual
            ├── AICopilot.tsx         # Chat interface
            └── RetrievalExplorer.tsx # Hybrid RAG explorer
```
