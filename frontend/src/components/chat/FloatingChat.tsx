'use client'

import { useState, useEffect } from 'react'
import ChatInterface from './ChatInterface'

export default function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    if (!isOpen) return
    const onEsc = (e: KeyboardEvent) => { if (e.key === 'Escape') setIsOpen(false) }
    document.addEventListener('keydown', onEsc)
    return () => document.removeEventListener('keydown', onEsc)
  }, [isOpen])

  return (
    <>
      {/* Panel */}
      {isOpen && (
        <>
          {/* Mobile backdrop */}
          <div className="fixed inset-0 z-40 bg-teal-950/40 sm:hidden" onClick={() => setIsOpen(false)} />

          {/* Chat panel */}
          <div className="fixed z-50 bg-white shadow-2xl shadow-teal-900/20 overflow-hidden animate-sheet-up
            sm:bottom-[76px] sm:right-5 sm:left-auto sm:w-[380px] sm:h-[560px] sm:max-h-[calc(100vh-96px)] sm:rounded-2xl sm:animate-chat-panel-in
            bottom-0 left-0 right-0 h-[82vh] rounded-t-2xl border border-teal-100">
            <ChatInterface onClose={() => setIsOpen(false)} />
          </div>
        </>
      )}

      {/* FAB */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close AI chat' : 'Open AI chat'}
        className={`fixed bottom-5 right-5 z-50 w-14 h-14 rounded-full cursor-pointer
          text-white shadow-lg flex items-center justify-center
          transition-all duration-200 active:scale-95 hover:scale-105
          ${isOpen
            ? 'bg-teal-700 hover:bg-teal-800 shadow-teal-900/30'
            : 'bg-teal-600 hover:bg-teal-700 shadow-teal-600/40 animate-pulse-ring'
          }`}
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>
    </>
  )
}
