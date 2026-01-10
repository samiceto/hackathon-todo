/**
 * Loading Component
 *
 * Displays a loading spinner with optional message.
 * Used for async operations like data fetching.
 */

interface LoadingProps {
  message?: string
  size?: 'small' | 'medium' | 'large'
  className?: string
}

export default function Loading({
  message = 'Loading...',
  size = 'medium',
  className = '',
}: LoadingProps) {
  const sizeClasses = {
    small: 'w-5 h-5',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  }

  const spinnerSize = sizeClasses[size]

  return (
    <div className={`flex flex-col items-center justify-center gap-4 p-8 ${className}`}>
      {/* Spinner */}
      <div className="relative">
        <svg
          className={`${spinnerSize} animate-spin text-primary-600`}
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>

      {/* Message */}
      {message && (
        <p className="text-sm text-gray-600 font-medium animate-pulse" aria-live="polite">
          {message}
        </p>
      )}

      {/* Screen reader text */}
      <span className="sr-only">Loading content, please wait</span>
    </div>
  )
}

/**
 * LoadingOverlay Component
 *
 * Full-screen loading overlay that covers the entire viewport.
 * Useful for page transitions or critical operations.
 */
export function LoadingOverlay({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <Loading message={message} size="large" />
    </div>
  )
}

/**
 * LoadingInline Component
 *
 * Inline loading spinner for button/form states.
 * No message, just the spinner.
 */
export function LoadingInline({ size = 'small' }: { size?: 'small' | 'medium' }) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6',
  }

  return (
    <svg
      className={`${sizeClasses[size]} animate-spin`}
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  )
}
