import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Database, Settings2, Bot, Search, Moon, Sun, Building2 } from 'lucide-react'
import clsx from 'clsx'

interface SidebarProps {
  darkMode: boolean
  onToggleDark: () => void
}

const nav = [
  { to: '/',           icon: LayoutDashboard, label: 'Overview' },
  { to: '/sources',    icon: Database,         label: 'Knowledge Sources' },
  { to: '/processing', icon: Settings2,        label: 'Data Processing' },
  { to: '/copilot',    icon: Bot,              label: 'AI Copilot' },
  { to: '/explorer',   icon: Search,           label: 'Retrieval Explorer' },
]

export default function Sidebar({ darkMode, onToggleDark }: SidebarProps) {
  return (
    <aside className="w-64 shrink-0 h-screen sticky top-0 flex flex-col border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
            <Building2 className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-white leading-tight">
              Enterprise Intelligence
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Copilot</p>
          </div>
        </div>
        <div className="mt-3 px-2 py-1 rounded bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
          <p className="text-[10px] text-amber-700 dark:text-amber-400 font-medium leading-tight">
            Demo Environment — Synthetic Data
          </p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-0.5 overflow-y-auto">
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
              )
            }
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-800">
        <button
          onClick={onToggleDark}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          {darkMode ? 'Light Mode' : 'Dark Mode'}
        </button>
        <p className="text-[10px] text-gray-400 dark:text-gray-600 px-3 mt-2">
          Acme Enterprise · v1.0.0
        </p>
      </div>
    </aside>
  )
}
