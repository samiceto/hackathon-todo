'use client'

import { useState, KeyboardEvent, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { voiceRecognition } from '@/lib/voice/voice-recognition'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
  initialValue?: string
}

export default function MessageInput({ onSend, disabled = false, placeholder = 'Ask about your tasks…', initialValue = '' }: MessageInputProps) {
  const { t } = useTranslation()
  const [message, setMessage] = useState(initialValue)
  const [isRecording, setIsRecording] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (initialValue) { setMessage(initialValue) }
  }, [initialValue])

  const autoResize = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`
  }

  const handleSend = () => {
    const trimmed = message.trim()
    if (trimmed && !disabled) {
      onSend(trimmed)
      setMessage('')
      if (textareaRef.current) textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const toggleRecording = () => {
    if (isRecording) {
      voiceRecognition.stop()
      setIsRecording(false)
    } else if (voiceRecognition.isBrowserSupported()) {
      setMessage('')
      setIsRecording(true)
      voiceRecognition.start(
        (transcript) => setMessage(transcript),
        () => setIsRecording(false),
        () => setIsRecording(false),
      )
    } else {
      alert('Speech recognition is not supported in your browser. Please try Chrome or Edge.')
    }
  }

  useEffect(() => { textareaRef.current?.focus() }, [])

  const canSend = !!message.trim() && !disabled && !isRecording

  return (
    <div className="border-t border-gray-100 bg-white px-3 py-2.5">
      <div className="flex items-end gap-1.5">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => { setMessage(e.target.value); autoResize() }}
          onKeyDown={handleKeyDown}
          disabled={disabled || isRecording}
          placeholder={isRecording ? 'Listening…' : placeholder}
          rows={1}
          className="flex-1 px-3 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-teal-100 focus:border-teal-400 resize-none disabled:bg-gray-50 disabled:cursor-not-allowed transition-all"
          style={{ minHeight: '36px', maxHeight: '120px' }}
        />

        {/* Voice */}
        <button
          onClick={toggleRecording}
          disabled={disabled}
          aria-label={isRecording ? t('messageInput.stopRecording') : t('messageInput.startVoiceRecording')}
          className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center transition-all ${
            isRecording ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
          } disabled:opacity-40 disabled:cursor-not-allowed`}
        >
          {isRecording ? (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          )}
        </button>

        {/* Send */}
        <button
          onClick={handleSend}
          disabled={!canSend}
          aria-label={t('messageInput.sendMessage')}
          className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center transition-all ${
            canSend ? 'bg-teal-600 text-white hover:bg-teal-700 active:scale-95' : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      <p className="text-[11px] text-gray-400 mt-1.5 px-1">
        <kbd className="px-1 py-0.5 bg-gray-100 rounded text-gray-500 font-mono text-[10px]">Enter</kbd> to send
        {' · '}
        <kbd className="px-1 py-0.5 bg-gray-100 rounded text-gray-500 font-mono text-[10px]">Shift+Enter</kbd> for new line
      </p>
    </div>
  )
}
