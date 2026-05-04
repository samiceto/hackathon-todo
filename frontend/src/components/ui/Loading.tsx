'use client'

interface LoadingProps {
  message?: string
  size?: 'small' | 'medium' | 'large'
  className?: string
}

const spinnerSize = { small: 'h-4 w-4', medium: 'h-6 w-6', large: 'h-8 w-8' }

export default function Loading({ message, size = 'medium', className = '' }: LoadingProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`} role="status">
      <svg className={`${spinnerSize[size]} animate-spin text-teal-500`} fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      {message && <p className="text-sm text-gray-500">{message}</p>}
      <span className="sr-only">Loading, please wait</span>
    </div>
  )
}

export function LoadingOverlay({ message }: { message?: string }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
      <Loading message={message} size="large" />
    </div>
  )
}

export function LoadingInline() {
  return (
    <svg className="h-4 w-4 animate-spin text-current" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
}

export function ErrorBoundaryMessage({ error, resetError }: { error: Error; resetError: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
      <div className="max-w-sm w-full text-center space-y-4">
        <p className="text-gray-900 font-semibold">Something went wrong</p>
        <p className="text-sm text-gray-500">{error.message || 'An unexpected error occurred.'}</p>
        <button onClick={resetError} className="px-4 py-2 bg-teal-600 text-white text-sm font-medium rounded-lg hover:bg-teal-700 transition-colors">
          Reload page
        </button>
      </div>
    </div>
  )
}
