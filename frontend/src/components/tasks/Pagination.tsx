'use client'

interface PaginationProps {
  currentPage: number
  totalPages: number
  totalItems: number
  pageSize: number
  onPageChange: (page: number) => void
}

export default function Pagination({ currentPage, totalPages, totalItems, pageSize, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null

  const start = (currentPage - 1) * pageSize + 1
  const end = Math.min(currentPage * pageSize, totalItems)

  const pages = (): (number | '...')[] => {
    if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
    if (currentPage <= 4) return [1, 2, 3, 4, 5, '...', totalPages]
    if (currentPage >= totalPages - 3) return [1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages]
    return [1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages]
  }

  const btnCls = 'w-8 h-8 flex items-center justify-center rounded-lg text-sm font-medium transition-all'

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mt-6 pt-4 border-t border-gray-100">
      <p className="text-xs text-gray-500">
        <span className="font-medium text-gray-700">{start}–{end}</span> of <span className="font-medium text-gray-700">{totalItems}</span> tasks
      </p>
      <div className="flex items-center gap-0.5">
        <button onClick={() => onPageChange(currentPage - 1)} disabled={currentPage === 1} aria-label="Previous page"
          className={`${btnCls} text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed`}>
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        {pages().map((p, i) => p === '...' ? (
          <span key={`e${i}`} className="w-8 text-center text-gray-400 text-xs">…</span>
        ) : (
          <button key={p} onClick={() => onPageChange(p as number)}
            className={`${btnCls} ${currentPage === p ? 'bg-teal-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-100'}`}
            aria-label={`Page ${p}`} aria-current={currentPage === p ? 'page' : undefined}>
            {p}
          </button>
        ))}
        <button onClick={() => onPageChange(currentPage + 1)} disabled={currentPage === totalPages} aria-label="Next page"
          className={`${btnCls} text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed`}>
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  )
}
