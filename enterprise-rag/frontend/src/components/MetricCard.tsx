import clsx from 'clsx'
import { LucideIcon } from 'lucide-react'

interface Props {
  label: string
  value: string | number
  icon: LucideIcon
  iconColor?: string
  sub?: string
  ready?: boolean
}

export default function MetricCard({ label, value, icon: Icon, iconColor = 'text-brand-600', sub, ready }: Props) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">{label}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
          {sub && <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{sub}</p>}
        </div>
        <div className={clsx('p-2.5 rounded-lg bg-gray-100 dark:bg-gray-800', iconColor)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      {ready !== undefined && (
        <div className="mt-3 flex items-center gap-1.5">
          <span className={clsx('w-2 h-2 rounded-full', ready ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600')} />
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {ready ? 'Ready' : 'Not ready'}
          </span>
        </div>
      )}
    </div>
  )
}
