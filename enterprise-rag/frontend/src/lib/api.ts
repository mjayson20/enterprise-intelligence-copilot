const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

// ── Types ────────────────────────────────────────────────────────────────────

export interface SourceInfo {
  filename: string
  source_type: string
  status: 'pending' | 'processing' | 'indexed' | 'error'
  chunks: number
  records: number
  pages: number
  last_processed: string | null
  error: string | null
  logs: string[]
}

export interface OverviewStats {
  total_sources: number
  indexed_sources: number
  total_chunks: number
  vector_count: number
  bm25_docs: number
  vector_db_ready: boolean
  bm25_ready: boolean
}

export interface OverviewResponse {
  app_name: string
  subtitle: string
  demo_notice: string
  stats: OverviewStats
  sources: Partial<SourceInfo>[]
  llm_configured: boolean
  llm_model: string
  llm_provider: string
}

export interface RetrievedChunk {
  chunk_id: string
  source_file: string
  source_type: string
  content: string
  metadata: Record<string, unknown>
  score: number
  rank: number
}

export interface RetrievalResult {
  query: string
  semantic_results: RetrievedChunk[]
  bm25_results: RetrievedChunk[]
  fused_results: RetrievedChunk[]
}

export interface Citation {
  source_file: string
  source_type: string
  metadata: Record<string, unknown>
  snippet: string
}

export interface QueryResponse {
  question: string
  answer: string
  citations: Citation[]
  retrieval: RetrievalResult
  model_used: string
}

// ── API calls ─────────────────────────────────────────────────────────────────

export const api = {
  overview: () => request<OverviewResponse>('/overview'),

  sources: {
    list: () => request<SourceInfo[]>('/sources'),
    get: (filename: string) => request<SourceInfo>(`/sources/${filename}`),
    process: (filename: string) =>
      request<{ message: string; status: string }>(`/sources/${encodeURIComponent(filename)}/process`, { method: 'POST' }),
    processAll: () =>
      request<{ message: string }>('/sources/process-all', { method: 'POST' }),
    upload: (file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return fetch(`${BASE}/sources/upload`, { method: 'POST', body: fd }).then(r => r.json())
    },
  },

  query: {
    ask: (question: string) =>
      request<QueryResponse>('/query/ask', {
        method: 'POST',
        body: JSON.stringify({ question }),
      }),
    retrieve: (query: string) =>
      request<RetrievalResult>('/query/retrieve', {
        method: 'POST',
        body: JSON.stringify({ query }),
      }),
  },
}
