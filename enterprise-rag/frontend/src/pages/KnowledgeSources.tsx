import { useEffect, useState, useRef } from 'react'
import { Upload, RefreshCw, Play, FileText, Table, Sheet } from 'lucide-react'
import { api, SourceInfo } from '../lib/api'
import StatusBadge from '../components/StatusBadge'

const typeIcon = (t: string) => {
  if (t === 'pdf') return <FileText className="w-4 h-4 text-red-500" />
  if (t === 'xlsx') return <Sheet className="w-4 h-4 text-emerald-600" />
  return <Table className="w-4 h-4 text-blue-500" />
}

const typeLabel = (t: string) =>
  t === 'pdf' ? 'PDF' : t === 'xlsx' ? 'Excel' : 'CSV'

export default function KnowledgeSources() {
  const [sources, setSources] = useState<SourceInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState<SourceInfo | null>(null)
  const [uploading, setUploading] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)

  const load = () => api.sources.list().then(setSources).catch(console.error)

  useEffect(() => {
    load()
    const t = setInterval(load, 3000)
    return () => clearInterval(t)
  }, [])

  const processAll = async () => {
    setLoading(true)
    await api.sources.processAll().catch(console.error)
    setLoading(false)
  }

  const processOne = async (filename: string) => {
    await api.sources.process(filename).catch(console.error)
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    await api.sources.upload(file).catch(console.error)
    setUploading(false)
    load()
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">Knowledge Sources</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">Manage and process enterprise data sources</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => fileInput.current?.click()} disabled={uploading} className="btn-secondary">
            <Upload className="w-4 h-4" />
            {uploading ? 'Uploading…' : 'Upload File'}
          </button>
          <input ref={fileInput} type="file" accept=".csv,.xlsx,.xls,.pdf" className="hidden" onChange={handleUpload} />
          <button onClick={processAll} disabled={loading} className="btn-primary">
            <Play className="w-4 h-4" />
            {loading ? 'Processing…' : 'Process All'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Source list */}
        <div className="lg:col-span-2 card overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-100 dark:border-gray-800">
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">All Sources</p>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 dark:border-gray-800">
                <th className="text-left px-5 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400">File</th>
                <th className="text-left px-3 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400">Type</th>
                <th className="text-left px-3 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400">Records</th>
                <th className="text-left px-3 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400">Chunks</th>
                <th className="text-left px-3 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400">Status</th>
                <th className="px-3 py-2.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
              {sources.map(src => (
                <tr
                  key={src.filename}
                  className="hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer"
                  onClick={() => setSelected(src)}
                >
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      {typeIcon(src.source_type)}
                      <span className="font-medium text-gray-800 dark:text-gray-200">{src.filename}</span>
                    </div>
                  </td>
                  <td className="px-3 py-3 text-gray-500 dark:text-gray-400">{typeLabel(src.source_type)}</td>
                  <td className="px-3 py-3 text-gray-700 dark:text-gray-300">
                    {src.source_type === 'pdf' ? `${src.pages}p` : src.records}
                  </td>
                  <td className="px-3 py-3 text-gray-700 dark:text-gray-300">{src.chunks}</td>
                  <td className="px-3 py-3"><StatusBadge status={src.status} /></td>
                  <td className="px-3 py-3">
                    <button
                      onClick={e => { e.stopPropagation(); processOne(src.filename) }}
                      className="p-1 text-gray-400 hover:text-brand-600 transition-colors"
                      title="Re-process"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Detail panel */}
        <div className="card p-5">
          {selected ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                {typeIcon(selected.source_type)}
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">{selected.filename}</h3>
              </div>
              <StatusBadge status={selected.status} />

              <div className="space-y-2 text-sm">
                {[
                  ['Type', typeLabel(selected.source_type)],
                  ['Records / Pages', selected.source_type === 'pdf' ? `${selected.pages} pages` : `${selected.records} rows`],
                  ['Chunks indexed', selected.chunks],
                  ['Last processed', selected.last_processed ? new Date(selected.last_processed).toLocaleString() : '—'],
                ].map(([k, v]) => (
                  <div key={String(k)} className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">{k}</span>
                    <span className="font-medium text-gray-800 dark:text-gray-200">{String(v)}</span>
                  </div>
                ))}
              </div>

              {selected.error && (
                <div className="p-2.5 rounded-lg bg-red-50 dark:bg-red-900/20 text-xs text-red-700 dark:text-red-400 font-mono break-all">
                  {selected.error}
                </div>
              )}

              {selected.logs.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Processing log</p>
                  <div className="bg-gray-950 rounded-lg p-3 space-y-0.5 max-h-48 overflow-y-auto">
                    {selected.logs.map((log, i) => (
                      <p key={i} className="text-xs text-gray-300 font-mono leading-relaxed">{log}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-40 text-center">
              <p className="text-gray-400 dark:text-gray-600 text-sm">Select a source to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
