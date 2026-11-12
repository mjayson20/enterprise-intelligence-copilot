import { useState } from 'react'
import { Search, Loader2, FileText, Table, Sheet, Zap } from 'lucide-react'
import { api, RetrievalResult, RetrievedChunk } from '../lib/api'
import clsx from 'clsx'

const SAMPLE_QUERIES = [
  'high priority support tickets',
  'DataSync Pro revenue sales',
  'P1 ticket SLA policy',
  'CUST-001 customer information',
  'CloudVault Enterprise features',
]

function ChunkCard({ chunk, mode }: { chunk: RetrievedChunk; mode: 'semantic' | 'bm25' | 'fused' }) {
  const [open, setOpen] = useState(false)
  const Icon = chunk.source_type === 'pdf' ? FileText : chunk.source_type === 'xlsx' ? Sheet : Table

  const colors = {
    semantic: 'border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-900/20',
    bm25:     'border-sky-200 dark:border-sky-800 bg-sky-50 dark:bg-sky-900/20',
    fused:    'border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20',
  }

  const scoreLabel = mode === 'fused' ? 'RRF' : mode === 'semantic' ? 'cos' : 'BM25'
  const meta = chunk.metadata as Record<string, unknown>

  let sourceDetail = ''
  if (chunk.source_type === 'pdf') sourceDetail = `Page ${meta.page ?? '?'}`
  else if (chunk.source_type === 'xlsx') sourceDetail = `Row ${meta.row_index ?? '?'}`

  return (
    <div className={clsx('rounded-xl border p-3.5 text-xs', colors[mode])}>
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <Icon className="w-3.5 h-3.5 text-gray-500 shrink-0" />
          <div>
            <p className="font-semibold text-gray-800 dark:text-gray-200">{chunk.source_file}</p>
            {sourceDetail && <p className="text-gray-500">{sourceDetail}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="px-1.5 py-0.5 rounded bg-white/60 dark:bg-black/20 font-mono text-gray-600 dark:text-gray-300">
            #{chunk.rank}
          </span>
          <span className="px-1.5 py-0.5 rounded bg-white/60 dark:bg-black/20 font-mono text-gray-600 dark:text-gray-300">
            {scoreLabel}: {chunk.score.toFixed(4)}
          </span>
        </div>
      </div>
      <button
        onClick={() => setOpen(!open)}
        className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 text-left w-full"
      >
        <p className={clsx('leading-relaxed', open ? '' : 'line-clamp-2')}>
          {chunk.content}
        </p>
        <span className="text-[10px] text-gray-400 mt-0.5">{open ? '▲ show less' : '▼ show more'}</span>
      </button>
    </div>
  )
}

function ResultColumn({
  title, subtitle, chunks, mode, color,
}: {
  title: string; subtitle: string; chunks: RetrievedChunk[]
  mode: 'semantic' | 'bm25' | 'fused'; color: string
}) {
  return (
    <div className="flex-1 min-w-0">
      <div className={clsx('px-4 py-2.5 rounded-t-xl border-x border-t', color)}>
        <p className="font-semibold text-sm">{title}</p>
        <p className="text-xs opacity-70">{subtitle}</p>
      </div>
      <div className="border-x border-b border-gray-200 dark:border-gray-800 rounded-b-xl p-3 space-y-2 max-h-[60vh] overflow-y-auto bg-white dark:bg-gray-900">
        {chunks.length === 0
          ? <p className="text-xs text-gray-400 text-center py-4">No results</p>
          : chunks.map(c => <ChunkCard key={c.chunk_id} chunk={c} mode={mode} />)
        }
      </div>
    </div>
  )
}

export default function RetrievalExplorer() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<RetrievalResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const search = async (q?: string) => {
    const qry = (q ?? query).trim()
    if (!qry) return
    setQuery(qry)
    setLoading(true)
    setError('')
    try {
      const r = await api.query.retrieve(qry)
      setResult(r)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Retrieval Explorer</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          Inspect Hybrid RAG — compare Semantic, BM25, and RRF-fused results side by side
        </p>
      </div>

      {/* Search */}
      <form onSubmit={e => { e.preventDefault(); search() }} className="flex gap-2">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Enter a retrieval query…"
          className="flex-1 px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button type="submit" disabled={loading || !query.trim()} className="btn-primary px-5">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          Search
        </button>
      </form>

      {/* Sample queries */}
      <div className="flex flex-wrap gap-2">
        {SAMPLE_QUERIES.map(q => (
          <button
            key={q}
            onClick={() => search(q)}
            className="px-3 py-1.5 text-xs rounded-full border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-brand-400 hover:text-brand-600 transition-colors"
          >
            {q}
          </button>
        ))}
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      {/* Results columns */}
      {result && (
        <div>
          {/* RRF explanation */}
          <div className="card p-4 mb-4 flex items-start gap-3">
            <Zap className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
            <div className="text-xs text-gray-600 dark:text-gray-400">
              <span className="font-semibold text-gray-800 dark:text-gray-200">Reciprocal Rank Fusion (RRF)</span>
              {' '}combines {result.semantic_results.length} semantic hits and {result.bm25_results.length} BM25 hits
              using RRF score = Σ 1/(k + rank) where k=60.
              Final context: top {result.fused_results.length} fused results sent to LLM.
            </div>
          </div>

          <div className="flex gap-4">
            <ResultColumn
              title="Semantic Search"
              subtitle={`Qdrant cosine · ${result.semantic_results.length} results`}
              chunks={result.semantic_results}
              mode="semantic"
              color="border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-200"
            />
            <ResultColumn
              title="BM25 Keywords"
              subtitle={`Okapi BM25 · ${result.bm25_results.length} results`}
              chunks={result.bm25_results}
              mode="bm25"
              color="border-sky-200 dark:border-sky-800 bg-sky-50 dark:bg-sky-900/30 text-sky-800 dark:text-sky-200"
            />
            <ResultColumn
              title="RRF Fusion"
              subtitle={`Final context · ${result.fused_results.length} results`}
              chunks={result.fused_results}
              mode="fused"
              color="border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200"
            />
          </div>
        </div>
      )}

      {!result && !loading && (
        <div className="card p-12 text-center">
          <Search className="w-8 h-8 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            Enter a query to see Semantic, BM25, and RRF-fused retrieval results
          </p>
        </div>
      )}
    </div>
  )
}
