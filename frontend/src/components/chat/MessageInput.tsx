/**
 * MessageInput Component
 *
 * Text input with send button and voice recording for composing chat messages.
 */

import { useState, KeyboardEvent, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { voiceRecognition } from '@/lib/voice/voice-recognition'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export default function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Type a message...',
}: MessageInputProps) {
  const { t } = useTranslation()
  const [message, setMessage] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const trimmed = message.trim()
    if (trimmed && !disabled) {
      onSend(trimmed)
      setMessage('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const toggleRecording = () => {
    if (isRecording) {
      // Stop recording
      voiceRecognition.stop()
      setIsRecording(false)
    } else {
      // Start recording
      if (voiceRecognition.isBrowserSupported()) {
        setMessage('') // Clear current text when starting to record
        setIsRecording(true)

        voiceRecognition.start(
          (transcript) => {
            setMessage(transcript)
          },
          (error) => {
            console.error('Speech recognition error', error)
            setIsRecording(false)
          },
          () => {
            setIsRecording(false)
          }
        )
      } else {
        alert('Speech recognition is not supported in your browser. Please try Chrome or Edge.')
      }
    }
  }

  // Auto-focus textarea when component mounts
  useEffect(() => {
    textareaRef.current?.focus()
  }, [])

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-4">
      <div className="flex gap-2 items-end">
        {/* Text Input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled || isRecording}
            placeholder={placeholder}
            rows={1}
            className="w-full px-4 py-3 pr-24 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none disabled:bg-gray-100 disabled:cursor-not-allowed transition-all"
            style={{
              minHeight: '48px',
              maxHeight: '120px',
            }}
          />

          {/* Character count (optional) */}
          {message.length > 0 && !isRecording && (
            <span className="absolute bottom-2 right-16 text-xs text-gray-400">
              {message.length}
            </span>
          )}
        </div>

        {/* Voice Recording Button */}
        <button
          onClick={toggleRecording}
          disabled={disabled}
          className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center transition-all mr-2 ${
            isRecording
              ? 'bg-red-500 text-white animate-pulse'
              : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          aria-label={isRecording ? t('messageInput.stopRecording') : t('messageInput.startVoiceRecording')}
          title={isRecording ? t('messageInput.stopRecording') : t('messageInput.voiceInput')}
        >
          {isRecording ? (
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          ) : (
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
          )}
        </button>

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim() || isRecording}
          className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center transition-all ${
            disabled || !message.trim() || isRecording
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-primary-600 text-white hover:bg-primary-700 active:scale-95'
          }`}
          aria-label={t('messageInput.sendMessage')}
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>

      {/* Helper Text */}
      <p className="text-xs text-gray-500 mt-2 px-1 flex justify-between">
        <span>
          {t('messageInput.enterToSend')}
          <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs ml-1">Enter</kbd>,
          <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs ml-1">Shift + Enter</kbd> {t('messageInput.shiftEnterForNewLine')}
        </span>
        {!isRecording && (
          <span className="ml-2">
            {t('messageInput.clickMicToSpeak')}
          </span>
        )}
        {isRecording && (
          <span className="ml-2 text-red-500 animate-pulse">
            {t('messageInput.listening')}
          </span>
        )}
      </p>
    </div>
  )
}
