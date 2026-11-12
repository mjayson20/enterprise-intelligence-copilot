import clsx from 'clsx'

interface Props {
  status: string
}

const config: Record<string, { label: string; className: string; dot: string }> = {
  indexed:    { label: 'Indexed',    className: 'status-indexed',    dot: 'bg-emerald-500' },
  processing: { label: 'Processing', className: 'status-processing', dot: 'bg-amber-500 animate-pulse' },
  pending:    { label: 'Pending',    className: 'status-pending',    dot: 'bg-gray-400' },
  error:      { label: 'Error',      className: 'status-error',      dot: 'bg-red-500' },
}

export default function StatusBadge({ status }: Props) {
  const cfg = config[status] ?? config.pending
  return (
    <span className={cfg.className}>
      <span className={clsx('w-1.5 h-1.5 rounded-full', cfg.dot)} />
      {cfg.label}
    </span>
  )
}
