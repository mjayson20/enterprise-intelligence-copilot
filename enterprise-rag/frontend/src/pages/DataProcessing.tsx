import { useEffect, useState } from 'react'
import { api, SourceInfo } from '../lib/api'
import { CheckCircle, Circle, Loader2, AlertCircle } from 'lucide-react'
import clsx from 'clsx'

const PIPELINE_STEPS = [
  { id: 'ingestion',   label: 'Data Ingestion',           desc: 'Load CSV, XLSX, and PDF files from sources' },
  { id: 'cleaning',    label: 'Cleaning & Normalisation',  desc: 'Remove duplicates, fill nulls, normalise fields' },
  { id: 'extraction',  label: 'OCR / Text Extraction',    desc: 'Extract text from PDFs; Tesseract OCR for image pages' },
  { id: 'metadata',    label: 'Metadata Extraction',      desc: 'Page numbers, row indices, source references' },
  { id: 'chunking',    label: 'Chunking',                 desc: 'Split text into overlapping 512-word chunks' },
  { id: 'embeddings',  label: 'Embedding Generation',     desc: 'Sentence Transformers (all-MiniLM-L6-v2) → 384-dim vectors' },
  { id: 'indexing',    label: 'Indexing',                 desc: 'Upsert vectors into Qdrant; build BM25 corpus' },
]

function stepForSource(logs: string[], stepIdx: number): 'done' | 'active' | 'waiting' | 'error' {
  const stepMarkers = ['Step 1/', 'Step 2/', 'Step 3/', 'Step 4/', 'Step 5/5']
  const logStr = logs.join(' ')
  const errored = logs.some(l => l.includes('✗'))

  if (errored && stepIdx <= 1) return 'error'

  // Rough heuristic: check if a later step started
  const currentStep = stepMarkers.reduce((acc, m, i) => logStr.includes(m) ? i : acc, -1)
  if (stepIdx < currentStep) return 'done'
  if (stepIdx === currentStep) return 'active'
  if (logStr.includes('✓ Source fully indexed')) return 'done'
  return 'waiting'
}

export default function DataProcessing() {
  const [sources, setSources] = useState<SourceInfo[]>([])
  const [selected, setSelected] = useState<string | null>(null)

  const load = () => api.sources.list().then(d => { setSources(d); if (!selected && d.length) setSelected(d[0].filename) }).catch(console.error)

  useEffect(() => {
    load()
    const t = setInterval(load, 2000)
    return () => clearInterval(t)
  }, [])

  const src = sources.find(s => s.filename === selected)

  const getStepStatus = (idx: number): 'done' | 'active' | 'waiting' | 'error' => {
    if (!src) return 'waiting'
    if (src.status === 'indexed') return 'done'
    if (src.status === 'error') return idx === 0 ? 'error' : 'waiting'
    if (src.status === 'pending') return 'waiting'
    return stepForSource(src.logs, idx)
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Data Processing</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          Visual pipeline status for each knowledge source
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Source selector */}
        <div className="card p-4 space-y-1">
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide px-1 mb-2">Sources</p>
          {sources.map(s => (
            <button
              key={s.filename}
              onClick={() => setSelected(s.filename)}
              className={clsx(
                'w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors',
                selected === s.filename
                  ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 font-medium'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
              )}
            >
              <span className="flex items-center justify-between">
                <span className="truncate">{s.filename}</span>
                {s.status === 'indexed' && <CheckCircle className="w-3.5 h-3.5 text-emerald-500 shrink-0" />}
                {s.status === 'processing' && <Loader2 className="w-3.5 h-3.5 text-amber-500 animate-spin shrink-0" />}
                {s.status === 'error' && <AlertCircle className="w-3.5 h-3.5 text-red-500 shrink-0" />}
              </span>
            </button>
          ))}
        </div>

        {/* Pipeline visual */}
        <div className="lg:col-span-2 space-y-4">
          {/* Step diagram */}
          <div className="card p-6">
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-5">
              Processing Pipeline — {selected ?? '…'}
            </p>
            <div className="space-y-0">
              {PIPELINE_STEPS.map((step, i) => {
                const status = getStepStatus(i)
                return (
                  <div key={step.id} className="flex items-start gap-4">
                    {/* Connector */}
                    <div className="flex flex-col items-center">
                      <div className={clsx(
                        'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all',
                        status === 'done'    && 'bg-emerald-500 border-emerald-500 text-white',
                        status === 'active'  && 'bg-amber-500 border-amber-500 text-white animate-pulse',
                        status === 'error'   && 'bg-red-500 border-red-500 text-white',
                        status === 'waiting' && 'bg-white dark:bg-gray-900 border-gray-300 dark:border-gray-700 text-gray-400',
                      )}>
                        {status === 'done'   ? <CheckCircle className="w-4 h-4" /> :
                         status === 'active' ? <Loader2 className="w-4 h-4 animate-spin" /> :
                         status === 'error'  ? <AlertCircle className="w-4 h-4" /> :
                         <Circle className="w-4 h-4" />}
                      </div>
                      {i < PIPELINE_STEPS.length - 1 && (
                        <div className={clsx(
                          'w-0.5 h-8 mt-0.5',
                          status === 'done' ? 'bg-emerald-300 dark:bg-emerald-800' : 'bg-gray-200 dark:bg-gray-800'
                        )} />
                      )}
                    </div>
                    {/* Label */}
                    <div className="pt-1.5 pb-4">
                      <p className={clsx(
                        'text-sm font-medium',
                        status === 'done'   ? 'text-emerald-700 dark:text-emerald-400' :
                        status === 'active' ? 'text-amber-700 dark:text-amber-400' :
                        status === 'error'  ? 'text-red-700 dark:text-red-400' :
                        'text-gray-500 dark:text-gray-500'
                      )}>
                        {step.label}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-600 mt-0.5">{step.desc}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Live log */}
          {src && src.logs.length > 0 && (
            <div className="card overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Processing Log</p>
                {src.status === 'processing' && (
                  <div className="flex items-center gap-1.5 text-xs text-amber-600 dark:text-amber-400">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    Live
                  </div>
                )}
              </div>
              <div className="bg-gray-950 p-4 max-h-52 overflow-y-auto">
                {src.logs.map((log, i) => (
                  <p key={i} className="text-xs text-gray-300 font-mono leading-relaxed">{log}</p>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          {src && src.status === 'indexed' && (
            <div className="card p-5">
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">Indexing Summary</p>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {src.source_type === 'pdf' ? src.pages : src.records}
                  </p>
                  <p className="text-xs text-gray-500">{src.source_type === 'pdf' ? 'Pages' : 'Records'}</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{src.chunks}</p>
                  <p className="text-xs text-gray-500">Chunks</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-emerald-600">✓</p>
                  <p className="text-xs text-gray-500">Indexed</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
