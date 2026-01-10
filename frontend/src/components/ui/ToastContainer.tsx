/**
 * ToastContainer Component
 *
 * Container for displaying multiple toast notifications with proper stacking.
 */

'use client'

import { createPortal } from 'react-dom'
import { useEffect, useState } from 'react'
import Toast, { ToastProps } from './Toast'

interface ToastContainerProps {
  toasts: Omit<ToastProps, 'onDismiss'>[]
  onDismiss: (id: string) => void
}

export default function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return createPortal(
    <div
      className="fixed top-4 right-4 z-[9999] flex flex-col gap-3 pointer-events-none"
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <Toast {...toast} onDismiss={onDismiss} />
        </div>
      ))}
    </div>,
    document.body
  )
}
