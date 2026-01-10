/**
 * useToast Hook
 *
 * Global toast notification management with TypeScript support.
 * Provides methods to show success, error, warning, and info toasts.
 */

'use client'

import { useContext } from 'react'
import { ToastContext } from '../contexts/ToastContext'
import { ToastVariant } from '@/components/ui/Toast'

export interface ShowToastOptions {
  message: string
  variant?: ToastVariant
  duration?: number
}

export function useToast() {
  const context = useContext(ToastContext)

  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }

  const { addToast, removeToast, toasts } = context

  const showToast = ({ message, variant = 'info', duration = 5000 }: ShowToastOptions) => {
    addToast({ message, variant, duration })
  }

  const success = (message: string, duration?: number) => {
    showToast({ message, variant: 'success', duration })
  }

  const error = (message: string, duration?: number) => {
    showToast({ message, variant: 'error', duration })
  }

  const warning = (message: string, duration?: number) => {
    showToast({ message, variant: 'warning', duration })
  }

  const info = (message: string, duration?: number) => {
    showToast({ message, variant: 'info', duration })
  }

  return {
    showToast,
    success,
    error,
    warning,
    info,
    dismiss: removeToast,
    toasts,
  }
}
