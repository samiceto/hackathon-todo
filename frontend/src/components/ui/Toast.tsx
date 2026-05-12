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

const config: Record<ToastVariant, { bar: string; icon: JSX.Element; text: string; bg: string; border: string }> = {
  success: {
    bar: 'bg-emerald-500',
    bg: 'bg-white',
    border: 'border-emerald-200',
    text: 'text-gray-800',
    icon: (
      <svg className="w-4 h-4 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    ),
  },
  error: {
    bar: 'bg-red-500',
    bg: 'bg-white',
    border: 'border-red-200',
    text: 'text-gray-800',
    icon: (
      <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
      </svg>
    ),
  },
  warning: {
    bar: 'bg-amber-500',
    bg: 'bg-white',
    border: 'border-amber-200',
    text: 'text-gray-800',
    icon: (
      <svg className="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
    ),
  },
  info: {
    bar: 'bg-teal-500',
    bg: 'bg-white',
    border: 'border-teal-200',
    text: 'text-gray-800',
    icon: (
      <svg className="w-4 h-4 text-teal-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
      </svg>
    ),
  },
}

export default function Toast({ id, message, variant, duration = 5000, onDismiss }: ToastProps) {
  const [isExiting, setIsExiting] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [progress, setProgress] = useState(100)
  const c = config[variant]

  useEffect(() => {
    if (duration === Infinity || isPaused) return
    const start = Date.now()
    const interval = setInterval(() => {
      const pct = Math.max(0, 100 - ((Date.now() - start) / duration) * 100)
      setProgress(pct)
      if (pct === 0) { setIsExiting(true); setTimeout(() => onDismiss(id), 250) }
    }, 50)
    return () => clearInterval(interval)
  }, [duration, isPaused, id, onDismiss])

  const dismiss = () => { setIsExiting(true); setTimeout(() => onDismiss(id), 250) }

  return (
    <div
      role="status"
      aria-live="polite"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      className={`relative w-80 overflow-hidden rounded-xl border shadow-lg ${c.bg} ${c.border} transition-all duration-250 ease-out
        ${isExiting ? 'opacity-0 translate-x-2 scale-95' : 'opacity-100 translate-x-0 scale-100 animate-slide-in-right'}`}
    >
      {/* Top accent bar */}
      <div className={`h-0.5 ${c.bar}`} />
      {/* Content */}
      <div className="flex items-start gap-3 px-4 py-3">
        <div className="flex-shrink-0 mt-0.5">{c.icon}</div>
        <p className={`flex-1 text-sm ${c.text} leading-snug`}>{message}</p>
        <button onClick={dismiss} className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors ml-1" aria-label="Dismiss">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      {/* Progress bar */}
      {duration !== Infinity && (
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-100">
          <div className={`h-full ${c.bar} opacity-60 transition-all duration-50 ease-linear`} style={{ width: `${progress}%` }} />
        </div>
      )}
    </div>
  )
}
