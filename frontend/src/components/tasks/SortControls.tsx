'use client'

export type SortField = 'created_at' | 'updated_at' | 'due_date' | 'priority' | 'title'

export interface SortOptions {
  sortBy: SortField | null
  sortOrder: 'asc' | 'desc'
}

interface SortControlsProps {
  onSortChange: (options: SortOptions) => void
  initialSort?: SortOptions
  compact?: boolean
}

const FIELDS: { value: SortField | ''; label: string }[] = [
  { value: '', label: 'Default' },
  { value: 'created_at', label: 'Date created' },
  { value: 'updated_at', label: 'Last updated' },
  { value: 'due_date', label: 'Due date' },
  { value: 'priority', label: 'Priority' },
  { value: 'title', label: 'Title (A–Z)' },
]

export default function SortControls({ onSortChange, initialSort = { sortBy: null, sortOrder: 'desc' } }: SortControlsProps) {
  return (
    <div className="flex items-center gap-2">
      <select
        value={initialSort.sortBy ?? ''}
        onChange={(e) => onSortChange({ sortBy: e.target.value === '' ? null : (e.target.value as SortField), sortOrder: initialSort.sortOrder })}
        className="h-8 flex-1 rounded-md border border-gray-200 bg-white px-2 text-xs text-gray-700 outline-none focus:border-teal-400 focus:ring-2 focus:ring-teal-100 transition-all"
        aria-label="Sort by"
      >
        {FIELDS.map((f) => <option key={f.value} value={f.value}>{f.label}</option>)}
      </select>
      {initialSort.sortBy && (
        <button
          onClick={() => onSortChange({ ...initialSort, sortOrder: initialSort.sortOrder === 'asc' ? 'desc' : 'asc' })}
          className="h-8 w-8 flex items-center justify-center rounded-md border border-gray-200 bg-white text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-all flex-shrink-0"
          aria-label={initialSort.sortOrder === 'asc' ? 'Sort descending' : 'Sort ascending'}
        >
          {initialSort.sortOrder === 'asc' ? (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
            </svg>
          ) : (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
            </svg>
          )}
        </button>
      )}
    </div>
  )
}
