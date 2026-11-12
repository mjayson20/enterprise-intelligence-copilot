import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Overview from './pages/Overview'
import KnowledgeSources from './pages/KnowledgeSources'
import DataProcessing from './pages/DataProcessing'
import AICopilot from './pages/AICopilot'
import RetrievalExplorer from './pages/RetrievalExplorer'

export default function App() {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950">
        <Sidebar darkMode={dark} onToggleDark={() => setDark(d => !d)} />
        <main className="flex-1 min-w-0">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/sources" element={<KnowledgeSources />} />
            <Route path="/processing" element={<DataProcessing />} />
            <Route path="/copilot" element={<AICopilot />} />
            <Route path="/explorer" element={<RetrievalExplorer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
