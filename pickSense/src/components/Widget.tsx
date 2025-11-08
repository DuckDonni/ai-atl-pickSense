import type { ReactNode } from 'react'

interface WidgetProps {
  id: string
  type: string
  title?: string
  children?: ReactNode
  onRemove?: (id: string) => void
}

export default function Widget({ id, type, title, children, onRemove }: WidgetProps) {
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <div className="flex items-center justify-between">
          <h2 className="card-title">{title || `Widget ${id}`}</h2>
          {onRemove && (
            <button 
              className="btn btn-sm btn-circle btn-ghost"
              onClick={() => onRemove(id)}
              aria-label="Remove widget"
            >
              ×
            </button>
          )}
        </div>
        <div className="mt-4">
          {children || <p className="text-base-content/70">Widget type: {type}</p>}
        </div>
      </div>
    </div>
  )
}