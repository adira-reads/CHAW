import clsx from 'clsx'

type Status = 'Y' | 'N' | 'A' | 'U' | null | undefined

interface StatusBadgeProps {
  status: Status
  size?: 'sm' | 'md' | 'lg'
  onClick?: () => void
  interactive?: boolean
}

const statusLabels: Record<string, string> = {
  Y: 'Passed',
  N: 'Not Yet',
  A: 'Absent',
  U: 'Unenrolled',
}

export default function StatusBadge({
  status,
  size = 'md',
  onClick,
  interactive = false,
}: StatusBadgeProps) {
  const sizeClasses = {
    sm: 'h-6 w-6 text-xs',
    md: 'h-8 w-8 text-sm',
    lg: 'h-10 w-10 text-base',
  }

  const statusClasses = {
    Y: 'status-y',
    N: 'status-n',
    A: 'status-a',
    U: 'status-u',
  }

  if (!status) {
    return (
      <span
        className={clsx(
          'inline-flex items-center justify-center rounded-full border-2 border-dashed border-gray-300 bg-gray-50 font-medium text-gray-400',
          sizeClasses[size],
          interactive && 'cursor-pointer hover:border-gray-400 hover:bg-gray-100'
        )}
        onClick={onClick}
      >
        -
      </span>
    )
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center justify-center rounded-full font-bold shadow-sm',
        sizeClasses[size],
        statusClasses[status] || 'bg-gray-400',
        interactive && 'cursor-pointer hover:opacity-80 active:scale-95 transition-all'
      )}
      onClick={onClick}
      title={statusLabels[status] || status}
    >
      {status}
    </span>
  )
}

// Status selector for lesson entry
interface StatusSelectorProps {
  currentStatus: Status
  onSelect: (status: 'Y' | 'N' | 'A' | 'U') => void
}

export function StatusSelector({ currentStatus, onSelect }: StatusSelectorProps) {
  const statuses: Array<'Y' | 'N' | 'A' | 'U'> = ['Y', 'N', 'A', 'U']

  return (
    <div className="flex gap-1">
      {statuses.map((status) => (
        <button
          key={status}
          onClick={() => onSelect(status)}
          className={clsx(
            'inline-flex h-10 w-10 items-center justify-center rounded-full font-bold transition-all',
            currentStatus === status
              ? clsx(
                  'ring-2 ring-offset-2',
                  status === 'Y' && 'status-y ring-status-passed',
                  status === 'N' && 'status-n ring-status-failed',
                  status === 'A' && 'status-a ring-status-absent',
                  status === 'U' && 'status-u ring-status-unenrolled'
                )
              : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
          )}
        >
          {status}
        </button>
      ))}
    </div>
  )
}
