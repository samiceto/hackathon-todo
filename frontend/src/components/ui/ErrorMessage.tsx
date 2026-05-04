'use client'

interface ErrorMessageProps {
  message: string
  title?: string
  severity?: 'error' | 'warning' | 'info'
  onRetry?: () => void
  retryText?: string
  className?: string
}

const styles = {
  error:   { bg: 'bg-red-50',   border: 'border-red-200',   text: 'text-red-700',   icon: 'text-red-500'   },
  warning: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: 'text-amber-500' },
  info:    { bg: 'bg-teal-50',  border: 'border-teal-200',  text: 'text-teal-700',  icon: 'text-teal-500'  },
}

export default function ErrorMessage({ message, title, severity = 'error', onRetry, retryText = 'Try again', className = '' }: ErrorMessageProps) {
  const s = styles[severity]
  return (
    <div role="alert" aria-live="assertive" className={`flex items-start gap-3 px-4 py-3 rounded-xl border animate-slide-up ${s.bg} ${s.border} ${className}`}>
      <svg className={`w-4 h-4 mt-0.5 flex-shrink-0 ${s.icon}`} fill="currentColor" viewBox="0 0 20 20">
        {severity === 'error' && <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />}
        {severity === 'warning' && <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />}
        {severity === 'info' && <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />}
      </svg>
      <div className="flex-1 min-w-0">
        {title && <p className={`text-sm font-semibold mb-0.5 ${s.text}`}>{title}</p>}
        <p className={`text-sm ${s.text}`}>{message}</p>
        {onRetry && (
          <button onClick={onRetry} className={`mt-2 text-xs font-semibold underline underline-offset-2 ${s.text} hover:opacity-80 transition-opacity`}>
            {retryText}
          </button>
        )}
      </div>
    </div>
  )
}

export function ErrorBoundaryMessage({ error, resetError }: { error: Error; resetError: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
      <div className="max-w-sm w-full">
        <ErrorMessage severity="error" title="Something went wrong" message={error.message || 'An unexpected error occurred.'} onRetry={resetError} retryText="Reload page" />
      </div>
    </div>
  )
}
