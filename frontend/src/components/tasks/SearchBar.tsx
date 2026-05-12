'use client'

import { useState, useEffect, useRef } from 'react'

interface SearchBarProps {
  onSearch: (query: string) => void
  debounceDelay?: number
  placeholder?: string
  initialValue?: string
}

export default function SearchBar({ onSearch, debounceDelay = 500, placeholder = 'Search tasks…', initialValue = '' }: SearchBarProps) {
  const [value, setValue] = useState(initialValue)
  const [isPending, setIsPending] = useState(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current)
    setIsPending(true)
    timerRef.current = setTimeout(() => { onSearch(value); setIsPending(false) }, debounceDelay)
    return () => { if (timerRef.current) clearTimeout(timerRef.current) }
  }, [value])

  const clear = () => { setValue(''); onSearch(''); setIsPending(false) }

  return (
    <div className="relative flex-1">
      <div className="pointer-events-none absolute inset-y-0 left-3 flex items-center">
        {isPending ? (
          <svg className="h-4 w-4 animate-spin text-teal-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        )}
      </div>
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter') { if (timerRef.current) clearTimeout(timerRef.current); onSearch(value); setIsPending(false) } }}
        placeholder={placeholder}
        aria-label="Search tasks"
        className="h-9 w-full rounded-lg border border-gray-200 bg-white pl-9 pr-8 text-sm text-gray-900 placeholder:text-gray-400 outline-none transition-all focus:border-teal-400 focus:ring-2 focus:ring-teal-100"
      />
      {value && (
        <button onClick={clear} className="absolute inset-y-0 right-2.5 flex items-center text-gray-400 hover:text-gray-600 transition-colors" aria-label="Clear search">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}
