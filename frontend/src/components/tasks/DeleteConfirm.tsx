'use client'

import { useEffect, useState } from 'react'

interface DeleteConfirmProps {
  isOpen: boolean
  taskTitle: string
  onConfirm: () => void
  onCancel: () => void
  isDeleting?: boolean
}

export default function DeleteConfirm({ isOpen, taskTitle, onConfirm, onCancel, isDeleting = false }: DeleteConfirmProps) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (isOpen) setTimeout(() => setVisible(true), 10)
    else setVisible(false)
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return
    const onEsc = (e: KeyboardEvent) => { if (e.key === 'Escape' && !isDeleting) onCancel() }
    document.addEventListener('keydown', onEsc)
    document.body.style.overflow = 'hidden'
    return () => { document.removeEventListener('keydown', onEsc); document.body.style.overflow = '' }
  }, [isOpen, isDeleting, onCancel])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={(e) => { if (e.target === e.currentTarget && !isDeleting) onCancel() }}>
      {/* Backdrop */}
      <div className={`absolute inset-0 bg-gray-900/50 transition-opacity duration-200 ${visible ? 'opacity-100' : 'opacity-0'}`} />

      {/* Modal */}
      <div className={`relative bg-white rounded-2xl shadow-xl w-full max-w-sm transform transition-all duration-200 ${visible ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}`}>
        <div className="p-6 text-center">
          {/* Icon */}
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>

          <h2 className="text-base font-semibold text-gray-900 mb-1">Delete task?</h2>
          <p className="text-sm text-gray-500 mb-6 px-2">
            "<span className="font-medium text-gray-700">{taskTitle}</span>" will be permanently removed.
          </p>

          <div className="flex gap-3">
            <button onClick={onCancel} disabled={isDeleting}
              className="flex-1 h-9 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              Cancel
            </button>
            <button onClick={onConfirm} disabled={isDeleting}
              className="flex-1 h-9 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2">
              {isDeleting ? (
                <><svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>Deleting…</>
              ) : 'Delete'}
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-3">Press <kbd className="px-1 py-0.5 bg-gray-100 rounded text-gray-500 font-mono text-xs">ESC</kbd> to cancel</p>
        </div>
      </div>
    </div>
  )
}
