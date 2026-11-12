import { useEffect, useState } from 'react'
import { Database, FileText, Layers, Cpu, CheckCircle, XCircle, Brain, BarChart3 } from 'lucide-react'
import { api, OverviewResponse } from '../lib/api'
import MetricCard from '../components/MetricCard'
import StatusBadge from '../components/StatusBadge'

export default function Overview() {
  const [data, setData] = useState<OverviewResponse | null>(null)
  const [error, setError] = useState('')

  const load = () =>
    api.overview().then(setData).catch(e => setError(e.message))

  useEffect(() => {
    load()
    const t = setInterval(load, 5000)
    return () => clearInterval(t)
  }, [])

  if (error) return (
    <div className="p-8 text-red-500">
      Cannot reach backend: {error}. Start the server with <code className="font-mono bg-gray-100 dark:bg-gray-800 px-1 rounded">uvicorn app.main:app --reload</code>
    </div>
  )

  if (!data) return <div className="p-8 text-gray-500">Loading…</div>

  const s = data.stats

  const sourceIcons: Record<string, string> = {
    csv:  '📊',
    xlsx: '📈',
    pdf:  '📄',
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 text-xs text-amber-700 dark:text-amber-400 font-medium mb-3">
          {data.demo_notice}
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{data.app_name}</h1>
        <p className="text-gray-500 dark:text-gray-400">{data.subtitle}</p>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Knowledge Sources" value={s.total_sources} icon={Database} iconColor="text-brand-600" sub={`${s.indexed_sources} indexed`} />
        <MetricCard label="Knowledge Chunks" value={s.total_chunks.toLocaleString()} icon={Layers} iconColor="text-violet-600" sub="across all sources" />
        <MetricCard label="Vector Embeddings" value={s.vector_count.toLocaleString()} icon={Brain} iconColor="text-indigo-600" ready={s.vector_db_ready} />
        <MetricCard label="BM25 Documents" value={s.bm25_docs.toLocaleString()} icon={BarChart3} iconColor="text-sky-600" ready={s.bm25_ready} />
      </div>

      {/* System status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Component status */}
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">System Components</h2>
          <div className="space-y-3">
            {[
              { label: 'CRM Data (CSV)', ready: data.sources.some(s => s.filename?.includes('crm') && s.status === 'indexed') },
              { label: 'Excel Data (XLSX)', ready: data.sources.some(s => s.source_type === 'xlsx' && s.status === 'indexed') },
              { label: 'PDF Documents', ready: data.sources.some(s => s.source_type === 'pdf' && s.status === 'indexed') },
              { label: 'Vector DB (Qdrant)', ready: s.vector_db_ready },
              { label: 'BM25 Keyword Index', ready: s.bm25_ready },
              { label: 'LLM (Groq)', ready: data.llm_configured },
            ].map(({ label, ready }) => (
              <div key={label} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
                <div className="flex items-center gap-1.5">
                  {ready
                    ? <><CheckCircle className="w-4 h-4 text-emerald-500" /><span className="text-xs text-emerald-600 dark:text-emerald-400">Ready</span></>
                    : <><XCircle className="w-4 h-4 text-gray-400" /><span className="text-xs text-gray-400">Not ready</span></>
                  }
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              LLM: <span className="font-mono">{data.llm_provider === 'groq' ? 'Groq' : data.llm_provider}</span> · <span className="font-mono">{data.llm_model}</span>
              {!data.llm_configured && <span className="text-amber-600 dark:text-amber-400 ml-2">— set GROQ_API_KEY in .env (free at console.groq.com/keys)</span>}
            </p>
          </div>
        </div>

        {/* Sources summary */}
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Data Sources</h2>
          <div className="space-y-2">
            {data.sources.map(src => (
              <div key={src.filename} className="flex items-center justify-between py-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-base">{sourceIcons[src.source_type ?? 'csv'] ?? '📁'}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{src.filename}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {src.source_type?.toUpperCase()} · {(src.records || src.pages || 0)} {src.source_type === 'pdf' ? 'pages' : 'records'}
                    </p>
                  </div>
                </div>
                <StatusBadge status={src.status ?? 'pending'} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Architecture overview */}
      <div className="card p-6">
        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-5">Primary Objective 01 — Core Pipeline</h2>
        <div className="flex flex-wrap items-center gap-2 text-xs font-medium">
          {[
            { label: 'CRM + Excel + PDF', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' },
            '→',
            { label: 'Data Ingestion', color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300' },
            '→',
            { label: 'Cleaning + OCR + Metadata', color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300' },
            '→',
            { label: 'Chunking + Embeddings', color: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300' },
            '→',
            { label: 'Semantic Search (Qdrant)', color: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300' },
            '+',
            { label: 'BM25 Keyword Search', color: 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-300' },
            '→',
            { label: 'RRF Fusion', color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300' },
            '→',
            { label: 'LLM', color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300' },
            '→',
            { label: 'Grounded Answer + Citations', color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' },
          ].map((item, i) =>
            typeof item === 'string'
              ? <span key={i} className="text-gray-400 dark:text-gray-600 font-bold">{item}</span>
              : <span key={i} className={`px-2.5 py-1 rounded-lg ${item.color}`}>{item.label}</span>
          )}
        </div>
      </div>
    </div>
  )
}
