'use client'

import { useState, useEffect } from 'react'

export interface FilterOptions {
  status?: 'completed' | 'incomplete' | null
  priority?: 'low' | 'medium' | 'high' | 'urgent' | null
  tags?: string[]
  dueDateStart?: string | null
  dueDateEnd?: string | null
}

interface FilterPanelProps {
  onFilterChange: (filters: FilterOptions) => void
  initialFilters?: FilterOptions
  isOpen?: boolean
}

const PRIORITY_OPTS = [
  { value: '',       label: 'All priorities' },
  { value: 'urgent', label: 'Urgent' },
  { value: 'high',   label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low',    label: 'Low' },
]

const selectCls = 'h-8 w-full rounded-lg border border-gray-200 bg-white px-2 text-xs text-gray-700 outline-none focus:border-teal-400 focus:ring-2 focus:ring-teal-100 transition-all hover:border-teal-300 cursor-pointer'
const inputCls  = 'h-8 w-full rounded-lg border border-gray-200 bg-white px-2 text-xs text-gray-700 placeholder:text-gray-400 outline-none focus:border-teal-400 focus:ring-2 focus:ring-teal-100 transition-all hover:border-teal-300'

export default function FilterPanel({ onFilterChange, initialFilters = {}, isOpen = true }: FilterPanelProps) {
  const [filters, setFilters] = useState<FilterOptions>(initialFilters)
  const [tagInput, setTagInput] = useState('')

  useEffect(() => { onFilterChange(filters) }, [filters])

  const set = (key: keyof FilterOptions, val: any) => setFilters((prev) => ({ ...prev, [key]: val }))
  const clearAll = () => { setFilters({}); setTagInput('') }

  const activeCount = Object.values(filters).filter(
    (v) => v !== null && v !== undefined && (Array.isArray(v) ? v.length > 0 : true)
  ).length

  if (!isOpen) return null

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <svg className="w-3.5 h-3.5 text-teal-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span className="text-xs font-semibold uppercase tracking-wide text-teal-700">Filters</span>
          {activeCount > 0 && (
            <span className="rounded-full bg-teal-100 px-1.5 py-0.5 text-xs font-bold text-teal-700">{activeCount}</span>
          )}
        </div>
        {activeCount > 0 && (
          <button onClick={clearAll} className="text-xs text-teal-500 hover:text-teal-700 font-medium transition-colors cursor-pointer">
            Clear all
          </button>
        )}
      </div>

      {/* Priority */}
      <div className="space-y-1">
        <label className="block text-xs font-semibold text-gray-600">Priority</label>
        <select
          value={filters.priority ?? ''}
          onChange={(e) => set('priority', e.target.value === '' ? null : e.target.value)}
          className={selectCls}
        >
          {PRIORITY_OPTS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      </div>

      {/* Tags */}
      <div className="space-y-1">
        <label className="block text-xs font-semibold text-gray-600">Tags</label>
        <input
          type="text"
          value={tagInput}
          onChange={(e) => {
            setTagInput(e.target.value)
            const tags = e.target.value.split(',').map((t) => t.trim()).filter(Boolean)
            set('tags', tags.length > 0 ? tags : undefined)
          }}
          placeholder="tag1, tag2…"
          className={inputCls}
        />
        <p className="text-xs text-teal-500/60">Tasks must have ALL tags</p>
      </div>

      {/* Due date range */}
      <div className="space-y-1">
        <label className="block text-xs font-semibold text-gray-600">Due date range</label>
        <div className="space-y-1.5">
          <input
            type="datetime-local"
            value={filters.dueDateStart ?? ''}
            onChange={(e) => set('dueDateStart', e.target.value || null)}
            className={inputCls}
            aria-label="From date"
          />
          <input
            type="datetime-local"
            value={filters.dueDateEnd ?? ''}
            onChange={(e) => set('dueDateEnd', e.target.value || null)}
            className={inputCls}
            aria-label="To date"
          />
        </div>
      </div>
    </div>
  )
}
