# PROJECT CONTEXT FILE
## Enterprise Intelligence Copilot — Complete Technical Reference
### Purpose: Drop this file into any LLM to get full project context for follow-up questions.

---

## SECTION 1 — WHAT IS THIS PROJECT? (Explain Like I'm 5)

Imagine you work at a company. The company has THREE kinds of important files:
- A spreadsheet (CSV) of all the customers
- An Excel file of all the sales
- PDF documents with company rules and policies

Now imagine someone asks: **"Which customers had the most sales AND have open support tickets?"**

To answer that, you'd normally open three different files, search through them manually, and piece together the answer yourself. That's slow and painful.

This project builds a **smart assistant** that:
1. Reads ALL those files automatically
2. Understands what's in them (not just keyword search — actual *meaning*)
3. Lets you type a question in plain English
4. Gives you a proper answer with exact citations like "I found this in sales_transactions.xlsx, Row 42"

That assistant is called **Enterprise Intelligence Copilot**.

The company is fake — called **"Acme Enterprise"**. All the data is synthetic (made up for demo purposes). This is a university Phase-1 prototype.

---

## SECTION 2 — THE COMPLETE FILE STRUCTURE

```
enterprise-rag/
│
├── data/                          ← All the raw data files
│   ├── generate_data.py           ← Python script that CREATES the fake data
│   ├── crm_customers.csv          ← 20 fake customers
│   ├── sales_transactions.xlsx    ← 200 fake sales transactions
│   ├── support_tickets.csv        ← 150 fake support tickets
│   └── documents/
│       ├── customer_policy.pdf    ← Company policy document
│       ├── support_policy.pdf     ← SLA rules (P1/P2/P3/P4)
│       ├── product_catalog.pdf    ← 9 product descriptions
│       └── invoice_samples.pdf    ← 4 sample invoices
│
├── backend/                       ← Python server (the brain)
│   ├── requirements.txt           ← Python packages needed
│   ├── .env                       ← Secret config (API keys)
│   ├── .env.example               ← Template for .env
│   └── app/
│       ├── main.py                ← FastAPI app entry point
│       ├── config.py              ← All settings/configuration
│       ├── models/
│       │   ├── chunk.py           ← Chunk data structure
│       │   └── retrieval.py       ← Response data structures
│       ├── routers/
│       │   ├── overview.py        ← GET /api/overview
│       │   ├── sources.py         ← /api/sources (list/upload/process)
│       │   └── query.py           ← /api/query/ask and /retrieve
│       └── services/
│           ├── data_processor.py  ← READS and CLEANS files
│           ├── vector_store.py    ← EMBEDS text + stores in Qdrant
│           ├── bm25_store.py      ← Keyword search index
│           ├── hybrid_retrieval.py← Combines both search types
│           ├── llm_service.py     ← Calls OpenAI for the answer
│           └── knowledge_base.py  ← Orchestrates the whole pipeline
│
├── frontend/                      ← React website (the face)
│   ├── package.json               ← Node.js packages
│   ├── vite.config.ts             ← Build tool config + dev proxy
│   ├── tailwind.config.js         ← CSS framework config
│   ├── index.html                 ← HTML entry point
│   └── src/
│       ├── main.tsx               ← React entry point
│       ├── App.tsx                ← Root component + routing
│       ├── index.css              ← Global styles + Tailwind
│       ├── lib/
│       │   └── api.ts             ← All backend API calls
│       ├── components/
│       │   ├── Sidebar.tsx        ← Left navigation bar
│       │   ├── StatusBadge.tsx    ← Colored status pill
│       │   └── MetricCard.tsx     ← Dashboard number card
│       └── pages/
│           ├── Overview.tsx          ← Dashboard page
│           ├── KnowledgeSources.tsx  ← Sources management page
│           ├── DataProcessing.tsx    ← Pipeline visual page
│           ├── AICopilot.tsx         ← Chat interface page
│           └── RetrievalExplorer.tsx ← Side-by-side retrieval page
│
└── README.md                      ← Project documentation
```

---

## SECTION 3 — THE TECH STACK (Every Tool Explained)

### FRONTEND TOOLS

**React 18**
- What: A JavaScript library for building websites
- Why here: Makes the UI components (chat bubbles, cards, tables) reusable and reactive
- Where: Every file in `frontend/src/`

**TypeScript**
- What: JavaScript but with types — you declare that a variable is a string, number, etc.
- Why here: Catches bugs before they happen. The `api.ts` file defines exact shapes of all API responses so TypeScript yells if something doesn't match.
- Where: All `.tsx` and `.ts` files

**Vite**
- What: The build tool and development server
- Why here: Extremely fast. Also has a "proxy" feature — when the frontend calls `/api/overview`, Vite forwards that to `http://localhost:8000/api/overview` automatically. This avoids CORS issues in development.
- Config: `vite.config.ts`

**Tailwind CSS**
- What: A CSS framework where you style things by adding class names like `bg-blue-500`, `text-sm`, `rounded-xl`
- Why here: Lets you build professional-looking UI without writing separate CSS files
- Config: `tailwind.config.js`
- Custom classes defined in `index.css`: `.card`, `.btn-primary`, `.btn-secondary`, `.status-indexed`, `.badge`

**React Router DOM**
- What: Handles navigation between pages without full page reloads
- Why here: The sidebar links (`/`, `/sources`, `/processing`, `/copilot`, `/explorer`) each load a different page component
- Where: `App.tsx` — `<BrowserRouter>`, `<Routes>`, `<Route>`

**Lucide React**
- What: Icon library — provides all the icons (Database, Bot, Search, Send, etc.)
- Why here: Clean, consistent icons for a professional look

**clsx**
- What: A tiny utility that combines CSS class names conditionally
- Why here: Used everywhere like `clsx('base-class', condition && 'extra-class')`

---

### BACKEND TOOLS

**Python 3.13**
- The programming language for the entire backend

**FastAPI**
- What: A modern Python web framework for building APIs
- Why here: Very fast, automatic API documentation at `/docs`, built-in request validation with Pydantic
- The app is defined in `main.py`
- Three routers: `overview.py`, `sources.py`, `query.py`

**Uvicorn**
- What: The ASGI server that actually runs FastAPI
- Why here: FastAPI needs a server to listen for HTTP requests — Uvicorn is that server
- Run command: `uvicorn app.main:app --reload --port 8000`

**Pydantic + pydantic-settings**
- What: Data validation library. Also reads `.env` files into Python settings.
- Why here: Every API request and response is validated automatically. `config.py` uses `BaseSettings` to read environment variables.
- The `Settings` class in `config.py` defines ALL configuration with defaults.

**Pandas**
- What: The standard Python library for working with spreadsheet-like data
- Why here: Reads CSV and XLSX files, handles cleaning (drop duplicates, fill nulls, strip whitespace)
- Where: `data_processor.py` — `process_csv()` and `process_xlsx()`

**OpenPyXL**
- What: Library for reading/writing Excel files
- Why here: Pandas uses it under the hood when calling `pd.ExcelFile()` on `.xlsx` files

**PyMuPDF (fitz)**
- What: Fast PDF reading library
- Why here: Opens PDF files and extracts text page by page with `page.get_text("text")`
- Where: `data_processor.py` — `process_pdf()`
- Also generates the PDFs in `generate_data.py` using `fitz.TextWriter`

**Tesseract OCR (pytesseract + Pillow)**
- What: Google's open-source OCR engine. Reads text from images.
- Why here: Some PDF pages might be scanned images (not real text). If `page.get_text()` returns fewer than 50 characters, it renders the page to a PNG image and runs Tesseract on it.
- Where: `data_processor.py` — `_ocr_page()`
- Status: Optional. If not installed, the fallback is silently skipped.

**Sentence Transformers (all-MiniLM-L6-v2)**
- What: A pre-trained neural network that converts text into a list of 384 numbers (a vector/embedding)
- Why this specific model: It's 90MB, runs on CPU, downloads once from HuggingFace, and produces high-quality semantic embeddings. "MiniLM" = distilled from a larger model (good quality, small size). "L6" = 6 transformer layers. "v2" = version 2.
- Where: `vector_store.py` — `_get_encoder()`
- Fallback: If PyTorch is not installed, a TF-IDF + random projection fallback (`_TfidfEncoder`) activates automatically

**Qdrant (in-memory)**
- What: A vector database — stores the 384-number embeddings and can find the most similar ones very fast
- Why in-memory: No Docker required for the MVP. The client runs as `QdrantClient(":memory:")` inside the Python process itself.
- Limitation: All vectors are lost when the Python process stops. They are re-created automatically on startup.
- Where: `vector_store.py`
- Collection name: `enterprise_rag`
- Distance metric: Cosine similarity

**rank-bm25 (BM25Okapi)**
- What: Implementation of the BM25 keyword ranking algorithm
- Why here: Complements the neural embeddings. Great at exact keyword matches, specific IDs, names.
- Where: `bm25_store.py`
- The entire BM25 index lives in Python memory as a list of tokenized chunks

**OpenAI Python SDK**
- What: The official Python client for OpenAI's API
- Why here: Sends the retrieved chunks + user question to GPT and gets back a grounded answer
- Model used: `gpt-4o-mini` (configurable via `.env`)
- Temperature: 0.1 (nearly deterministic — no creative hallucination)
- Where: `llm_service.py`

**python-dotenv**
- What: Loads `.env` files into environment variables
- Where: Used automatically by `pydantic-settings`

**python-multipart**
- What: Enables FastAPI to accept file uploads
- Where: Used in `sources.py` for the upload endpoint

**numpy**
- What: Numerical computing library
- Where: Used in `bm25_store.py` for `np.argsort()` to find top-k scores, and in the TF-IDF fallback encoder

**scikit-learn**
- What: Machine learning library
- Where: Only used in the `_TfidfEncoder` fallback class in `vector_store.py` — `TfidfVectorizer`

---

## SECTION 4 — THE SYNTHETIC DATA (What's in the Files)

All data was generated by `data/generate_data.py` using Python's `random` module with seed 42 (so it's reproducible).

### crm_customers.csv — 20 rows
Columns: `customer_id, customer_name, industry, region, account_manager, annual_revenue, employee_count, customer_since, account_status`

Customer IDs: CUST-001 through CUST-020
Companies: Apex Logistics, Blue Horizon Tech, Cascade Manufacturing, Delta Financial, Eagle Retail Group, Frontier Healthcare, Global Shipping Co, Harbor Industries, Ironclad Security, Jade Pharmaceuticals, Keystone Analytics, Lighthouse Media, Meridian Consulting, Northern Grid Energy, Orbit Software, Pacific Ventures, Quantum Dynamics, Riverstone Mining, Summit Aerospace, Titan Construction

Account statuses: Active (70%), At Risk (20%), Churned (10%)
Revenue range: $500,000 to $50,000,000

### sales_transactions.xlsx — 200 rows (Sheet: "Sales")
Columns: `transaction_id, customer_id, product, sales_date, quantity, unit_price, sales_amount, region, sales_rep, status`

Transaction IDs: TXN-0001 through TXN-0200
Products: DataSync Pro, CloudVault Enterprise, SecureEdge Suite, AnalyticsCore, ConnectAPI Platform, AutoScale Engine, ReportMaster, DataSync Basic, CloudVault Standard
Statuses: Closed Won (65%), Closed Lost (20%), Pending (15%)
customer_id links to crm_customers.csv

### support_tickets.csv — 150 rows
Columns: `ticket_id, customer_id, issue_type, priority, product, created_date, status, resolution_time_hours, description`

Ticket IDs: TKT-0001 through TKT-0150
Priorities: P1 (10%), P2 (25%), P3 (40%), P4 (25%)
Statuses: Resolved (75%), Open or In Progress (25%)
customer_id links to crm_customers.csv

### 4 PDF Documents
- **customer_policy.pdf**: Customer tier classification (Tier 1/2/3 by revenue), onboarding steps, at-risk criteria, compliance
- **support_policy.pdf**: P1/P2/P3/P4 definitions, SLA times (P1 Enterprise = 15 min response, 2 hr resolution), escalation path, SLA breach credits
- **product_catalog.pdf**: 9 products with prices, features, target customers
- **invoice_samples.pdf**: 4 sample invoices for CUST-001, CUST-002, CUST-004, CUST-010

**Cross-source linking**: The customer IDs (CUST-001 etc.) appear in ALL data sources. This means a query about "CUST-001" can pull matching chunks from the CRM CSV, Sales XLSX, Support Tickets CSV, and Invoice PDF simultaneously.

---

## SECTION 5 — THE COMPLETE PIPELINE (How Data Flows)

### Phase A: Processing (happens once on startup, or when you click "Process All")

```
FILE ON DISK
    │
    ▼ data_processor.py — process_file()
    │
    ├─ If .csv  → process_csv()
    │   • pd.read_csv(path, dtype=str)
    │   • drop_duplicates()
    │   • fillna("N/A")
    │   • strip whitespace
    │   • Each row → text block "customer_id: CUST-001\ncustomer_name: Apex Logistics\n..."
    │
    ├─ If .xlsx → process_xlsx()
    │   • pd.ExcelFile(path)
    │   • Iterate sheets
    │   • Same cleaning as CSV
    │   • Records row_index for citations
    │
    └─ If .pdf  → process_pdf()
        • fitz.open(path)
        • page.get_text("text") for each page
        • If text < 50 chars → _ocr_page() with Tesseract
        • Records page number for citations
    │
    ▼ _clean_text()
    │   • Remove control characters
    │   • Collapse multiple spaces
    │   • Collapse 3+ newlines
    │
    ▼ _split_text()  [CHUNKING]
    │   • Split into words
    │   • Sliding window: 512 words per chunk
    │   • 64-word overlap between consecutive chunks
    │   • Each chunk becomes a Chunk object
    │
    ▼ Chunk object created
    │   • chunk_id: UUID
    │   • source_file: "crm_customers.csv"
    │   • source_type: "csv" | "xlsx" | "pdf"
    │   • content: the 512-word text
    │   • metadata: {row_index, customer_id, page, sheet, etc.}
    │
    ├─ vector_store.embed_and_index(chunks)
    │   • all-MiniLM-L6-v2 encodes each chunk → 384-dim vector
    │   • Qdrant.upsert() stores vector + payload
    │
    └─ bm25_store.index_chunks(chunks)
        • Tokenize each chunk: re.findall(r"\b[a-z0-9]+\b", text.lower())
        • Add to BM25Okapi corpus
        • Rebuild BM25 index
```

**Result: 382 chunks indexed** (20 CRM + 200 Sales + 150 Support + ~12 PDF)

---

### Phase B: Querying (happens on every user question)

```
USER TYPES: "What is the support policy for P1 tickets?"
    │
    ▼ POST /api/query/ask  (query.py router)
    │
    ├─── SEMANTIC SEARCH (vector_store.py)
    │     • Encode query → 384-dim vector using all-MiniLM-L6-v2
    │     • Qdrant.search(query_vector, limit=10)
    │     • Returns top-10 chunks by cosine similarity
    │     • Scores: 0.0 to 1.0 (1.0 = identical meaning)
    │
    ├─── BM25 KEYWORD SEARCH (bm25_store.py)
    │     • Tokenize query: ["support", "policy", "p1", "tickets"]
    │     • BM25Okapi.get_scores(tokens) → score for each of 382 docs
    │     • np.argsort(scores)[::-1][:10] → top-10 chunks by keyword match
    │     • Scores: 0.0 to ~15.0 (raw BM25 values)
    │
    ▼ RECIPROCAL RANK FUSION (hybrid_retrieval.py)
    │
    │   For each chunk, calculate:
    │   RRF_score = 1/(60 + rank_in_semantic) + 1/(60 + rank_in_bm25)
    │
    │   Example chunk ranked #1 semantic, #2 BM25:
    │   RRF = 1/(60+1) + 1/(60+2) = 0.01639 + 0.01613 = 0.03252
    │
    │   Example chunk ranked #5 semantic only (not in BM25):
    │   RRF = 1/(60+5) = 0.01538
    │
    │   Sort all candidates by RRF score → take top 6
    │
    ▼ TOP-6 FUSED CHUNKS (the "context")
    │
    ▼ LLM SERVICE (llm_service.py)
    │   • Build context block: "[Context 1] Source: support_policy.pdf (Page 2)\n<text>"
    │   • System prompt: "Answer ONLY from the provided context. Cite sources."
    │   • POST to OpenAI: gpt-4o-mini, temperature=0.1, max_tokens=1500
    │   • Extract citations from chunk metadata
    │
    ▼ RESPONSE RETURNED TO FRONTEND
        {
          "question": "...",
          "answer": "P1 tickets require...",
          "citations": [...],
          "retrieval": {
            "semantic_results": [...10 chunks...],
            "bm25_results": [...10 chunks...],
            "fused_results": [...6 chunks...]
          },
          "model_used": "gpt-4o-mini"
        }
```

---

## SECTION 6 — THE 5 FRONTEND PAGES IN DETAIL

### Page 1: Overview (`/`)
**File**: `pages/Overview.tsx`
**What it does**: Dashboard showing system health
- Polls `GET /api/overview` every 5 seconds
- Shows 4 metric cards: Sources, Chunks, Vector Embeddings, BM25 Documents
- Shows a component status grid (CRM ✓, Excel ✓, PDF ✓, Vector DB ✓, BM25 ✓, LLM ✓/✗)
- Shows a pipeline diagram as colored badges
- Shows per-source status table

### Page 2: Knowledge Sources (`/sources`)
**File**: `pages/KnowledgeSources.tsx`
**What it does**: Manage data sources
- Lists all 7 sources in a table with type, record count, chunk count, status badge
- Click a row → detail panel shows logs, error messages, last processed time
- "Process All" button → `POST /api/sources/process-all`
- "Upload File" button → `POST /api/sources/upload` with multipart form
- Individual re-process button (↻ icon) → `POST /api/sources/{filename}/process`
- Polls every 3 seconds to show live processing status

### Page 3: Data Processing (`/processing`)
**File**: `pages/DataProcessing.tsx`
**What it does**: Visual pipeline with live logs
- Left panel: list of all 7 sources, click to select one
- Right panel: 7-step pipeline diagram with colored circles
  - Done = green checkmark
  - Active = amber spinning loader
  - Waiting = gray empty circle
  - Error = red alert icon
- The step status is inferred from the processing logs by checking which "Step X/5" messages have appeared
- Live log panel shows the raw server logs in a dark terminal-style box
- Summary card shows record/page count and chunk count after indexing

### Page 4: AI Copilot (`/copilot`)
**File**: `pages/AICopilot.tsx`
**What it does**: Chat interface
- 6 sample question buttons on the empty state
- Chat messages: user = blue bubble right-aligned, assistant = white bubble left-aligned
- Loading = 3 bouncing dots animation
- Each assistant message has expandable Citation Cards below it
  - Shows source filename + page/row detail
  - Click to expand the raw snippet text
- Footer shows model used and chunk count
- Calls `POST /api/query/ask`

### Page 5: Retrieval Explorer (`/explorer`)
**File**: `pages/RetrievalExplorer.tsx`
**What it does**: Shows the Hybrid RAG in action
- Most important for demos — proves the system is NOT faking retrieval
- Three columns side by side:
  - **Blue column**: Semantic Search results (cosine scores)
  - **Sky column**: BM25 results (BM25 scores)
  - **Amber column**: RRF Fused results (RRF scores)
- Each chunk card shows: source file, page/row, rank number, score, expandable text
- RRF explanation banner at top shows the formula
- 5 sample query buttons
- Calls `POST /api/query/retrieve` (no LLM, retrieval only)

---

## SECTION 7 — THE MODELS IN DETAIL

### Model 1: all-MiniLM-L6-v2 (Sentence Transformer)
- **Type**: Neural network (transformer architecture)
- **Parameters**: ~22 million
- **Download size**: ~90MB (cached at `~/.cache/huggingface/`)
- **Input**: Any text string (max ~256 words effectively)
- **Output**: 384-dimensional float32 vector
- **Training**: Pre-trained on large text datasets to produce "semantic" embeddings — texts with similar meaning cluster together in vector space
- **Library**: `sentence-transformers` Python package
- **Loaded in**: `vector_store.py` → `_get_encoder()` → `SentenceTransformer("all-MiniLM-L6-v2")`
- **Used for**: Both indexing (encoding all 382 chunks) and querying (encoding the search query)
- **Fallback**: `_TfidfEncoder` class — uses sklearn TF-IDF + random projection to 384 dims. Works but produces lower quality results. Activates automatically if torch/transformers fails.

### Model 2: Qdrant (Vector Database)
- **Type**: Not a model — a vector similarity search engine
- **Mode**: In-memory (`QdrantClient(":memory:")`)
- **Distance metric**: Cosine similarity
- **Vector dimensions**: 384 (matches all-MiniLM-L6-v2 output)
- **What it stores**: Each vector + a "payload" dict containing the full chunk content and metadata
- **Search**: Given a query vector, returns the N most similar vectors using approximate nearest neighbor search
- **Library**: `qdrant-client` Python package
- **Limitation**: In-memory means data is lost on restart. All 382 chunks are re-indexed automatically on every startup (takes ~5-10 seconds).

### Model 3: BM25 Okapi
- **Type**: Statistical ranking algorithm (not neural)
- **Year invented**: 1994
- **What it is**: A term frequency-inverse document frequency variant
- **Formula**: `score(D,Q) = Σ IDF(qi) × f(qi,D)×(k1+1) / (f(qi,D) + k1×(1-b+b×|D|/avgdl))`
  - k1=1.5 (term saturation — diminishing returns after many occurrences)
  - b=0.75 (length normalization — shorter docs get a small boost)
  - IDF = log((N - df + 0.5)/(df + 0.5) + 1) where N=total docs, df=docs containing term
- **Tokenization**: `re.findall(r"\b[a-z0-9]+\b", text.lower())` — lowercase words and numbers only
- **Library**: `rank_bm25` Python package, `BM25Okapi` class
- **Index**: Rebuilt from scratch every time a new source is indexed (efficient enough for 382 docs)

### Model 4: Reciprocal Rank Fusion (RRF)
- **Type**: Rank aggregation algorithm (not neural, no parameters to learn)
- **Formula**: `RRF(d) = Σ 1/(k + rank(d))` where k=60 (configured in `config.py` as `rrf_k`)
- **Why k=60**: Empirically found to work well across many IR benchmarks. Smooths out differences between rank 1 and rank 2 (both get similar scores instead of rank 1 dominating).
- **Deduplication**: If the same chunk appears in both lists, its scores are accumulated (not double-counted as two separate results)
- **Output**: Sorted, deduplicated list of up to 6 chunks (configured as `final_top_k=6`)
- **Implemented in**: `hybrid_retrieval.py` → `reciprocal_rank_fusion()`

### Model 5: GPT-4o-mini (OpenAI)
- **Type**: Large Language Model (Generative AI)
- **Provider**: OpenAI API (cloud, not local)
- **Configured by**: `OPENAI_MODEL=gpt-4o-mini` in `.env`
- **Temperature**: 0.1 — very low, near-deterministic responses
- **Max tokens**: 1500
- **System prompt**: Strictly grounded — "Answer ONLY from the provided context. Do not use outside knowledge. If insufficient info, say so."
- **Input to LLM**: System prompt + "Question: X" + formatted context block of 6 chunks
- **Output**: Natural language answer with inline citations
- **Graceful fallback**: If `OPENAI_API_KEY` is empty, `_fallback_answer()` returns the raw chunks as the "answer" — retrieval still works perfectly.

---

## SECTION 8 — CONFIGURATION (config.py + .env)

All settings are in `backend/app/config.py` via `pydantic_settings.BaseSettings`.

```python
class Settings(BaseSettings):
    # LLM
    openai_api_key: str = ""          # REQUIRED for LLM answers
    openai_model: str = "gpt-4o-mini" # Change to "gpt-4o" for higher quality

    # Qdrant
    qdrant_use_memory: bool = True    # False = connect to external Qdrant server
    qdrant_host: str = "localhost"    # Only used if qdrant_use_memory = False
    qdrant_port: int = 6333           # Default Qdrant port
    qdrant_collection: str = "enterprise_rag"

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384          # MUST match model output size

    # Chunking
    chunk_size: int = 512             # Words per chunk
    chunk_overlap: int = 64           # Words shared between consecutive chunks

    # Retrieval
    semantic_top_k: int = 10          # Semantic candidates fetched
    bm25_top_k: int = 10             # BM25 candidates fetched
    final_top_k: int = 6             # Final chunks after RRF
    rrf_k: int = 60                  # RRF smoothing constant
```

---

## SECTION 9 — API ENDPOINTS

All endpoints served at `http://localhost:8000`

| Method | Path | What it does |
|--------|------|-------------|
| GET | `/api/health` | Returns `{"status":"ok"}` — health check |
| GET | `/api/overview` | Returns system stats, all source statuses, LLM config |
| GET | `/api/sources` | Lists all 7 sources with status/chunks/logs |
| GET | `/api/sources/{filename}` | Gets single source detail |
| POST | `/api/sources/{filename}/process` | Triggers re-processing of one source |
| POST | `/api/sources/process-all` | Triggers processing of all sources |
| POST | `/api/sources/upload` | Uploads a new CSV/XLSX/PDF file |
| POST | `/api/query/ask` | Full RAG pipeline — returns answer + citations + retrieval |
| POST | `/api/query/retrieve` | Retrieval only — returns semantic/BM25/fused results, no LLM |

Auto-generated API docs available at: `http://localhost:8000/docs`

---

## SECTION 10 — HOW THE FRONTEND TALKS TO THE BACKEND

The frontend is a React app running at `http://localhost:5174`.
The backend is a Python FastAPI server running at `http://localhost:8000`.

**Vite Proxy** (`vite.config.ts`):
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```
This means: when the frontend calls `/api/overview`, Vite forwards it to `http://localhost:8000/api/overview`. The browser never directly talks to port 8000 — it always goes through Vite on port 5174.

**API Client** (`src/lib/api.ts`):
```typescript
const BASE = '/api'
async function request<T>(path: string, options?: RequestInit): Promise<T>
```
All API calls go through this typed wrapper. TypeScript interfaces (`SourceInfo`, `QueryResponse`, `RetrievalResult`, etc.) exactly mirror the Pydantic models on the backend.

**Polling**: The Overview and KnowledgeSources pages call `setInterval(load, 3000)` or `setInterval(load, 5000)` to refresh data every few seconds. This is how processing status updates appear live.

---

## SECTION 11 — CURRENT SYSTEM STATE (as of last run)

| Item | Status |
|------|--------|
| Backend | Running at http://localhost:8000 |
| Frontend | Running at http://localhost:5174 |
| Total chunks indexed | 382 |
| CRM (crm_customers.csv) | 20 rows → 20 chunks |
| Sales (sales_transactions.xlsx) | 200 rows → 200 chunks |
| Support (support_tickets.csv) | 150 rows → 150 chunks |
| PDFs (4 files) | ~12 chunks total |
| Qdrant | In-memory, 382 vectors (384-dim cosine) |
| BM25 | In-memory, 382 documents |
| Embedding model | all-MiniLM-L6-v2, loaded and cached |
| OpenAI LLM | NOT configured (OPENAI_API_KEY is empty in .env) |
| LLM fallback | Active — shows raw retrieved context instead of AI answer |

**To enable full AI answers**: Open `backend/.env` and set:
```
OPENAI_API_KEY=sk-your-key-here
```
The backend hot-reloads automatically (because `--reload` flag is active) and LLM answers will work immediately.

**Important**: Because Qdrant is in-memory, every time the backend process restarts, it re-indexes all 382 chunks automatically. This takes about 5-15 seconds depending on CPU speed.

---

## SECTION 12 — WHAT'S MISSING / FUTURE IMPROVEMENTS

These are things that would make this go from a prototype to a real production system:

### Immediate (Phase 2 of the university project)

**1. Persistent Vector Storage**
- Currently: Qdrant in-memory — everything lost on restart
- Fix: Run Qdrant as a Docker container or use Qdrant Cloud
- Code change: Set `QDRANT_USE_MEMORY=false` in `.env` and set `QDRANT_HOST`, `QDRANT_PORT`

**2. PostgreSQL Database**
- Currently: All state (source registry, chunk counts, logs) lives in Python memory dicts
- Fix: Add SQLAlchemy + PostgreSQL. Store `Source`, `Chunk`, `ProcessingLog` as DB tables
- Why: Survives restarts, queryable, proper ACID transactions

**3. Real Authentication**
- Currently: Zero authentication — anyone with the URL can access everything
- Fix: Add JWT tokens, user login, role-based access control

**4. Better Chunking Strategy**
- Currently: Naive sliding window on word count (512 words, 64 overlap)
- Fix: Semantic chunking — split on sentence boundaries, paragraph boundaries, or use a model to detect topic shifts
- Also: Increase PDF chunk count — current PDFs produce very few chunks because the content is short

**5. Streaming LLM Responses**
- Currently: The UI shows bouncing dots until the full answer arrives (could be 5-10 seconds)
- Fix: Use OpenAI's streaming API (`stream=True`) and Server-Sent Events to send tokens to the frontend as they arrive

### Medium Term

**6. Evaluation & Quality Metrics**
- No way to measure if retrieval is actually good
- Add: RAGAS framework for RAG evaluation (context precision, recall, answer faithfulness)
- Add: User feedback (thumbs up/down on answers)

**7. Cross-Source Aggregation**
- Currently: The LLM gets 6 chunks and answers based on them
- Problem: A question like "which customers have highest sales?" requires aggregating ALL 200 sales rows, not just the 6 most similar ones
- Fix: Add a SQL/Pandas "structured query" layer that runs actual aggregations on the raw data before or instead of vector search

**8. Document Re-indexing**
- Currently: Re-processing a source appends new chunks to the existing index (duplicates possible)
- Fix: When re-processing, delete old vectors for that source from Qdrant before adding new ones
- Code change: `embed_and_index(chunks, recreate=True)` with source-level filtering

**9. Metadata Filtering in Semantic Search**
- Currently: Semantic search searches ALL 382 chunks regardless of source
- Fix: Qdrant supports payload filtering — "search only in support_tickets.csv" or "search only PDFs"
- This would improve precision for source-specific questions

**10. Better PDF Processing**
- Currently: PDFs use basic `page.get_text()` — tables in PDFs are extracted as flat text, losing structure
- Fix: Use `pdfplumber` or `camelot` for table extraction, preserve column/row relationships

### Long Term

**11. Multi-Modal Support**
- Add support for images, PowerPoints, Word documents
- Vision models for diagrams and charts

**12. Fine-tuned Embedding Model**
- all-MiniLM-L6-v2 is a general-purpose model
- Fine-tuning it on enterprise-specific data (same domain vocabulary) would improve retrieval quality significantly

**13. Graph-Based Knowledge Representation**
- Instead of flat chunks, build a knowledge graph where CUST-001 is a node connected to its sales, tickets, and invoice nodes
- Graph RAG would allow multi-hop reasoning ("customers managed by Sarah Chen who have open P1 tickets")

**14. Agentic Workflows**
- Instead of one-shot RAG, use an LLM agent that can decide WHICH data source to query, run multiple retrievals, and synthesize
- Tools: LangChain Agents, LangGraph, or custom tool-calling with OpenAI function calling

**15. Caching**
- Cache frequent query results (Redis or in-memory dict) to avoid re-running retrieval and LLM for the same questions

---

## SECTION 13 — HOW TO RUN FROM SCRATCH

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip

### Steps

```bash
# 1. Go to project
cd enterprise-rag

# 2. Generate synthetic data
cd data
pip install pandas openpyxl PyMuPDF
python generate_data.py
cd ..

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Add OpenAI key (optional but needed for AI answers)
# Edit backend/.env and set OPENAI_API_KEY=sk-...

# 5. Start backend
uvicorn app.main:app --reload --port 8000
# Wait for "Application startup complete" and indexing to finish (~15 sec)

# 6. In a NEW terminal, install and start frontend
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173 (or 5174 if 5173 is taken)
```

---

## SECTION 14 — KEY DECISIONS AND TRADE-OFFS MADE

| Decision | What was chosen | Alternative | Why this choice |
|----------|----------------|-------------|----------------|
| Vector DB | Qdrant in-memory | Chroma, Pinecone, Weaviate | No Docker needed, runs in-process, easy MVP |
| Embedding model | all-MiniLM-L6-v2 | OpenAI text-embedding-ada-002, nomic-embed | Free, local, 90MB, fast CPU inference |
| BM25 library | rank-bm25 | Elasticsearch, Whoosh, Lucene | Simple, pure Python, no server needed |
| LLM | OpenAI gpt-4o-mini | Ollama local models, Anthropic Claude | Most accessible for demo, configurable |
| Chunking | Sliding window 512w/64overlap | Semantic chunking, recursive text splitter | Simplest implementation, good enough |
| Frontend | React + Vite | Next.js, Vue, Svelte | Standard choice, Vite proxy avoids CORS |
| Backend | FastAPI | Django, Flask, Express | Async, auto-docs, fast, Pydantic validation |
| State storage | Python in-memory dicts | PostgreSQL, SQLite | No DB setup needed for MVP |
| Data format | CSV + XLSX + PDF | JSON, SQL, NoSQL | Realistic enterprise data formats |

---

## SECTION 15 — KNOWN LIMITATIONS OF CURRENT BUILD

1. **In-memory only**: Restart = re-index (takes ~15 seconds). Not a bug — intentional MVP choice.
2. **No LLM without API key**: Without `OPENAI_API_KEY`, answers show raw retrieved text. Retrieval works fine.
3. **PDF chunk count is low**: The 4 PDFs produce only ~12 chunks total because the synthetic PDF content is short. Real PDFs would produce hundreds of chunks.
4. **No deduplication on re-index**: Processing a file twice adds duplicate vectors. Workaround: restart the backend.
5. **BM25 has no persistence**: Same as Qdrant — rebuilt on startup.
6. **Sequential processing**: All 7 sources are processed one after another. Could be parallelized.
7. **Vite proxy only works in dev**: In production build, you'd need nginx or similar to proxy `/api` to port 8000.
8. **Font loading from Google CDN**: The Inter and JetBrains Mono fonts load from Google Fonts (requires internet). For offline demo, use local fonts.

---

## SECTION 16 — EXAMPLE QUESTIONS AND EXPECTED BEHAVIOR

| Question | Which sources get retrieved | What the answer should say |
|----------|----------------------------|---------------------------|
| "What is the support policy for P1 tickets?" | support_policy.pdf pages 1-2 | 15 min response (Tier 1), 30 min (Tier 2), 2hr resolution (Tier 1) |
| "Which customers generated the highest sales?" | sales_transactions.xlsx | Top customers by sales_amount (aggregated from transaction rows) |
| "Summarize CUST-001" | crm_customers.csv, sales_transactions.xlsx, support_tickets.csv, invoice_samples.pdf | Apex Logistics, Logistics industry, invoice ~$121k, sales history, support tickets |
| "What products are available?" | product_catalog.pdf | DataSync Pro $4999/mo, CloudVault Enterprise $2999/mo, etc. |
| "Which customers are At Risk?" | crm_customers.csv | List of customers with account_status = "At Risk" |
| "What is the P1 SLA breach penalty?" | support_policy.pdf | 10% service credit applied automatically |

---

*This file was auto-generated from the actual source code of the Enterprise Intelligence Copilot project.*
*Last updated: September 2026*
*Project type: University Final Year Project, Phase 1 Prototype*
*Data: 100% synthetic — Acme Enterprise is a fictional company*
