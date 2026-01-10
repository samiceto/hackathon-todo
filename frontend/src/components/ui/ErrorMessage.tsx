/**
 * ErrorMessage Component
 *
 * Displays error messages with appropriate styling and icons.
 * Supports different severity levels and optional retry actions.
 */

interface ErrorMessageProps {
  message: string
  title?: string
  severity?: 'error' | 'warning' | 'info'
  onRetry?: () => void
  retryText?: string
  className?: string
}

export default function ErrorMessage({
  message,
  title,
  severity = 'error',
  onRetry,
  retryText = 'Try again',
  className = '',
}: ErrorMessageProps) {
  const severityStyles = {
    error: {
      container: 'bg-red-50 border-red-200',
      icon: 'text-red-600',
      title: 'text-red-900',
      message: 'text-red-800',
      button: 'bg-red-600 hover:bg-red-700 text-white',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      icon: 'text-yellow-600',
      title: 'text-yellow-900',
      message: 'text-yellow-800',
      button: 'bg-yellow-600 hover:bg-yellow-700 text-white',
    },
    info: {
      container: 'bg-blue-50 border-blue-200',
      icon: 'text-blue-600',
      title: 'text-blue-900',
      message: 'text-blue-800',
      button: 'bg-blue-600 hover:bg-blue-700 text-white',
    },
  }

  const styles = severityStyles[severity]

  return (
    <div
      className={`p-4 rounded-xl border-2 ${styles.container} animate-slide-up ${className}`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`flex-shrink-0 ${styles.icon} mt-0.5`}>
          {severity === 'error' && (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          )}
          {severity === 'warning' && (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          )}
          {severity === 'info' && (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>

        {/* Content */}
        <div className="flex-1">
          {title && (
            <h3 className={`text-sm font-semibold mb-1 ${styles.title}`}>{title}</h3>
          )}
          <p className={`text-sm ${styles.message}`}>{message}</p>

          {/* Retry Button */}
          {onRetry && (
            <button
              onClick={onRetry}
              className={`mt-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${styles.button} focus:outline-none focus:ring-4 focus:ring-opacity-20`}
              aria-label={retryText}
            >
              {retryText}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * ErrorBoundaryMessage Component
 *
 * Full-page error display for error boundary scenarios.
 */
export function ErrorBoundaryMessage({
  error,
  resetError,
}: {
  error: Error
  resetError: () => void
}) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <div className="max-w-md w-full">
        <ErrorMessage
          severity="error"
          title="Something went wrong"
          message={error.message || 'An unexpected error occurred. Please try again.'}
          onRetry={resetError}
          retryText="Reload page"
        />
      </div>
    </div>
  )
}

/**
 * NetworkErrorMessage Component
 *
 * Specialized error message for network/API failures.
 */
export function NetworkErrorMessage({
  onRetry,
  message = 'Unable to connect to the server. Please check your internet connection and try again.',
}: {
  onRetry?: () => void
  message?: string
}) {
  return (
    <ErrorMessage
      severity="error"
      title="Connection Error"
      message={message}
      onRetry={onRetry}
      retryText="Retry"
    />
  )
}

/**
 * NotFoundMessage Component
 *
 * Specialized error message for 404 scenarios.
 */
export function NotFoundMessage({
  resource = 'resource',
  onGoBack,
}: {
  resource?: string
  onGoBack?: () => void
}) {
  return (
    <ErrorMessage
      severity="warning"
      title="Not Found"
      message={`The ${resource} you're looking for doesn't exist or has been removed.`}
      onRetry={onGoBack}
      retryText="Go back"
    />
  )
}
