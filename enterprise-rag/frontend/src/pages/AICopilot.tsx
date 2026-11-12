import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, FileText, Table, Sheet, ChevronDown, ChevronUp } from 'lucide-react'
import { api, QueryResponse, Citation } from '../lib/api'
import clsx from 'clsx'

const SAMPLE_QUESTIONS = [
  'Which customers generated the highest sales?',
  'Which high-value customers have unresolved high-priority support tickets?',
  'What is the support policy for P1 tickets?',
  'Which products generate the most revenue?',
  'Summarize the information available about customer CUST-001.',
  'Compare customer revenue with support ticket volume.',
]

function CitationCard({ c }: { c: Citation }) {
  const [open, setOpen] = useState(false)
  const Icon = c.source_type === 'pdf' ? FileText : c.source_type === 'xlsx' ? Sheet : Table
  const meta = c.metadata as Record<string, unknown>

  let detail = ''
  if (c.source_type === 'pdf')  detail = `Page ${meta.page ?? '?'}`
  if (c.source_type === 'xlsx') detail = `Sheet: ${meta.sheet ?? '?'}, Row: ${meta.row_index ?? '?'}`
  if (c.source_type === 'csv')  detail = meta.customer_id ? `ID: ${meta.customer_id}` : ''

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden text-xs">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 dark:bg-gray-800/50 text-left"
      >
        <div className="flex items-center gap-2">
          <Icon className="w-3.5 h-3.5 text-gray-500" />
          <span className="font-medium text-gray-700 dark:text-gray-300">{c.source_file}</span>
          {detail && <span className="text-gray-400 dark:text-gray-500">· {detail}</span>}
        </div>
        {open ? <ChevronUp className="w-3.5 h-3.5 text-gray-400" /> : <ChevronDown className="w-3.5 h-3.5 text-gray-400" />}
      </button>
      {open && (
        <div className="px-3 py-2 bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 font-mono leading-relaxed">
          {c.snippet}
        </div>
      )}
    </div>
  )
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  response?: QueryResponse
}

export default function AICopilot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (question: string) => {
    if (!question.trim() || loading) return
    const q = question.trim()
    setInput('')
    setMessages(m => [...m, { role: 'user', content: q }])
    setLoading(true)

    try {
      const res = await api.query.ask(q)
      setMessages(m => [...m, { role: 'assistant', content: res.answer, response: res }])
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      setMessages(m => [...m, { role: 'assistant', content: `Error: ${msg}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-0px)]">
      {/* Header */}
      <div className="px-8 py-5 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">AI Copilot</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Ask questions across all enterprise data sources</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <div className="w-12 h-12 rounded-2xl bg-brand-600 flex items-center justify-center mx-auto mb-3">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Enterprise Intelligence Copilot</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Ask questions across CRM, Sales, Support, and Policy documents
              </p>
            </div>
            <p className="text-xs font-semibold text-gray-400 dark:text-gray-600 uppercase tracking-wide mb-3">Sample Questions</p>
            <div className="grid gap-2">
              {SAMPLE_QUESTIONS.map(q => (
                <button
                  key={q}
                  onClick={() => send(q)}
                  className="text-left px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-800 text-sm text-gray-700 dark:text-gray-300 hover:border-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900/20 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={clsx('flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}
            <div className={clsx('max-w-2xl', msg.role === 'user' ? 'order-first' : '')}>
              <div className={clsx(
                'px-4 py-3 rounded-2xl text-sm leading-relaxed',
                msg.role === 'user'
                  ? 'bg-brand-600 text-white rounded-tr-sm'
                  : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-sm'
              )}>
                <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
              </div>

              {/* Citations */}
              {msg.response && msg.response.citations.length > 0 && (
                <div className="mt-3 space-y-1.5">
                  <p className="text-xs font-semibold text-gray-400 dark:text-gray-600 uppercase tracking-wide">
                    Sources ({msg.response.citations.length})
                  </p>
                  {msg.response.citations.map((c, ci) => (
                    <CitationCard key={ci} c={c} />
                  ))}
                </div>
              )}

              {msg.response && (
                <p className="text-[10px] text-gray-400 dark:text-gray-600 mt-1.5 px-1">
                  Model: {msg.response.model_used} · {msg.response.retrieval.fused_results.length} chunks retrieved
                </p>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-4 h-4 text-gray-600 dark:text-gray-300" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="px-4 py-3 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl rounded-tl-sm">
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-8 py-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <form
          onSubmit={e => { e.preventDefault(); send(input) }}
          className="flex gap-3 max-w-3xl mx-auto"
        >
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask a question about your enterprise data…"
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent disabled:opacity-50"
          />
          <button type="submit" disabled={loading || !input.trim()} className="btn-primary px-4 py-3">
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  )
}
