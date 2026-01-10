/**
 * DeleteConfirm Modal Component
 *
 * A beautiful confirmation dialog for task deletion with smooth animations.
 * Features backdrop blur, scale entrance, and micro-interactions.
 */

'use client'

import { useEffect, useState } from 'react'

interface DeleteConfirmProps {
  isOpen: boolean
  taskTitle: string
  onConfirm: () => void
  onCancel: () => void
  isDeleting?: boolean
}

export default function DeleteConfirm({
  isOpen,
  taskTitle,
  onConfirm,
  onCancel,
  isDeleting = false,
}: DeleteConfirmProps) {
  const [isVisible, setIsVisible] = useState(false)

  // Handle animation states
  useEffect(() => {
    if (isOpen) {
      // Slight delay for smooth entrance
      setTimeout(() => setIsVisible(true), 10)
    } else {
      setIsVisible(false)
    }
  }, [isOpen])

  // Handle ESC key press
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isDeleting) {
        onCancel()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, isDeleting, onCancel])

  // Don't render if not open
  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={(e) => {
        // Close on backdrop click (only if not deleting)
        if (e.target === e.currentTarget && !isDeleting) {
          onCancel()
        }
      }}
    >
      {/* Backdrop with blur effect */}
      <div
        className={`
          absolute inset-0 bg-gray-900/60 backdrop-blur-sm
          transition-opacity duration-300 ease-out
          ${isVisible ? 'opacity-100' : 'opacity-0'}
        `}
      />

      {/* Modal Card */}
      <div
        className={`
          relative bg-white rounded-2xl shadow-2xl
          max-w-md w-full
          transform transition-all duration-300 ease-out
          ${isVisible ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}
        `}
      >
        {/* Decorative top border - danger gradient */}
        <div className="h-1.5 bg-gradient-to-r from-red-500 via-rose-500 to-red-600 rounded-t-2xl" />

        <div className="p-6 sm:p-7">
          {/* Icon with pulsing animation */}
          <div className="flex items-center justify-center mb-5">
            <div className="relative">
              {/* Pulsing background ring */}
              <div className="absolute inset-0 bg-red-100 rounded-full animate-ping opacity-75" />

              {/* Icon container */}
              <div className="relative w-16 h-16 bg-gradient-to-br from-red-500 to-rose-600 rounded-full flex items-center justify-center shadow-lg shadow-red-500/30">
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2.5}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
            Delete Task?
          </h2>

          {/* Description */}
          <p className="text-gray-600 text-center mb-6 leading-relaxed">
            Are you sure you want to delete{' '}
            <span className="font-semibold text-gray-900 break-words">
              "{taskTitle}"
            </span>
            ? This action cannot be undone.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col-reverse sm:flex-row gap-3">
            {/* Cancel Button */}
            <button
              onClick={onCancel}
              disabled={isDeleting}
              className="
                flex-1 px-5 py-3
                bg-gray-100 hover:bg-gray-200
                text-gray-700 font-semibold rounded-xl
                transition-all duration-200 ease-out
                focus:outline-none focus:ring-4 focus:ring-gray-200
                disabled:opacity-50 disabled:cursor-not-allowed
                hover:scale-[1.02] active:scale-[0.98]
              "
            >
              Cancel
            </button>

            {/* Delete Button */}
            <button
              onClick={onConfirm}
              disabled={isDeleting}
              className="
                flex-1 px-5 py-3
                bg-gradient-to-br from-red-500 to-rose-600
                hover:from-red-600 hover:to-rose-700
                text-white font-bold rounded-xl
                shadow-lg shadow-red-500/30
                transition-all duration-200 ease-out
                focus:outline-none focus:ring-4 focus:ring-red-200
                disabled:opacity-70 disabled:cursor-not-allowed
                hover:scale-[1.02] active:scale-[0.98]
                flex items-center justify-center gap-2
              "
            >
              {isDeleting ? (
                <>
                  {/* Loading Spinner */}
                  <svg
                    className="w-5 h-5 animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="3"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>
                  Deleting...
                </>
              ) : (
                <>
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2.5}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                  Delete Task
                </>
              )}
            </button>
          </div>

          {/* Hint text */}
          <p className="text-xs text-gray-400 text-center mt-4">
            Press <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600 font-mono">ESC</kbd> to cancel
          </p>
        </div>
      </div>
    </div>
  )
}
