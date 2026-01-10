/**
 * Toast Component - Refined Modern Design
 *
 * Individual toast notification with glassmorphism, smooth animations,
 * and auto-dismiss functionality with visual progress indicator.
 */

'use client'

import { useEffect, useState } from 'react'

export type ToastVariant = 'success' | 'error' | 'warning' | 'info'

export interface ToastProps {
  id: string
  message: string
  variant: ToastVariant
  duration?: number
  onDismiss: (id: string) => void
}

const variantStyles = {
  success: {
    gradient: 'from-emerald-500 to-green-600',
    bg: 'bg-emerald-50/95',
    border: 'border-emerald-200',
    text: 'text-emerald-900',
    icon: 'text-emerald-600',
    progress: 'bg-emerald-500',
  },
  error: {
    gradient: 'from-red-500 to-rose-600',
    bg: 'bg-red-50/95',
    border: 'border-red-200',
    text: 'text-red-900',
    icon: 'text-red-600',
    progress: 'bg-red-500',
  },
  warning: {
    gradient: 'from-amber-500 to-orange-600',
    bg: 'bg-amber-50/95',
    border: 'border-amber-200',
    text: 'text-amber-900',
    icon: 'text-amber-600',
    progress: 'bg-amber-500',
  },
  info: {
    gradient: 'from-blue-500 to-indigo-600',
    bg: 'bg-blue-50/95',
    border: 'border-blue-200',
    text: 'text-blue-900',
    icon: 'text-blue-600',
    progress: 'bg-blue-500',
  },
}

const icons = {
  success: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
        clipRule="evenodd"
      />
    </svg>
  ),
  error: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
        clipRule="evenodd"
      />
    </svg>
  ),
  warning: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
        clipRule="evenodd"
      />
    </svg>
  ),
  info: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
        clipRule="evenodd"
      />
    </svg>
  ),
}

export default function Toast({
  id,
  message,
  variant,
  duration = 5000,
  onDismiss,
}: ToastProps) {
  const [isExiting, setIsExiting] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [progress, setProgress] = useState(100)

  const styles = variantStyles[variant]

  useEffect(() => {
    if (duration === Infinity || isPaused) return

    const startTime = Date.now()
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime
      const remaining = Math.max(0, 100 - (elapsed / duration) * 100)
      setProgress(remaining)

      if (remaining === 0) {
        handleDismiss()
      }
    }, 16) // ~60fps

    return () => clearInterval(interval)
  }, [duration, isPaused, id])

  const handleDismiss = () => {
    setIsExiting(true)
    setTimeout(() => onDismiss(id), 300) // Match animation duration
  }

  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      className={`
        relative overflow-hidden
        w-full max-w-sm
        backdrop-blur-xl ${styles.bg}
        border-2 ${styles.border}
        rounded-2xl shadow-2xl
        transform transition-all duration-300 ease-out
        ${
          isExiting
            ? 'opacity-0 scale-95 translate-x-8'
            : 'opacity-100 scale-100 translate-x-0 animate-slide-in-right'
        }
        hover:shadow-3xl hover:scale-[1.02]
      `}
    >
      {/* Gradient accent bar */}
      <div className={`h-1 bg-gradient-to-r ${styles.gradient}`} />

      {/* Content */}
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className={`flex-shrink-0 ${styles.icon}`}>
            {icons[variant]}
          </div>

          {/* Message */}
          <p className={`flex-1 text-sm font-medium ${styles.text} leading-relaxed`}>
            {message}
          </p>

          {/* Dismiss button */}
          <button
            onClick={handleDismiss}
            className={`
              flex-shrink-0 -mr-1 -mt-1 p-1.5
              rounded-lg transition-colors
              ${styles.icon} hover:bg-black/5
              focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-current
            `}
            aria-label="Dismiss notification"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Progress bar */}
      {duration !== Infinity && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/5">
          <div
            className={`h-full ${styles.progress} transition-all duration-100 ease-linear`}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}
