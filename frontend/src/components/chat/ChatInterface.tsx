/**
 * ChatInterface Component
 *
 * Main chat interface integrating MessageList and MessageInput.
 * Handles message sending, streaming responses, and conversation management.
 */

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslation } from 'react-i18next'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import { ChatMessage, chatkitApi } from '@/lib/api/chatkit'
import { useToast } from '@/lib/hooks/useToast'
import authClient from '@/lib/auth/auth-client'
import { useI18n } from '@/contexts/I18nContext'

export default function ChatInterface() {
  const { t } = useTranslation()
  const { language } = useI18n()
  const router = useRouter()
  const toast = useToast()

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streamingMessage, setStreamingMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [threadId, setThreadId] = useState<string | undefined>(undefined)

  // Check authentication on mount
  useEffect(() => {
    const user = authClient.getCurrentUser()
    if (!user) {
      router.push('/signin')
    }
  }, [router])

  // Handle sending a message
  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: text,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])

    setIsLoading(true)
    setStreamingMessage('')

    try {
      // Stream response from backend
      let fullResponse = ''

      for await (const chunk of chatkitApi.streamResponse(text, threadId, language)) {
        fullResponse += chunk
        setStreamingMessage(fullResponse)
      }

      // Add assistant message to messages list
      if (fullResponse) {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: fullResponse,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      }

      setStreamingMessage('')
    } catch (error: any) {
      console.error(t('chatInterface.errorProcessing'), error)

      // Show error toast
      toast.error(error.message || t('chatInterface.failedToSend'))

      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: t('chatInterface.errorProcessing'),
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle creating a new conversation
  const handleNewConversation = () => {
    setMessages([])
    setThreadId(undefined)
    setStreamingMessage('')
    toast.success(t('chatInterface.startedNewConversation'))
  }

  return (
    <div
      className="flex flex-col h-full bg-gray-50 rounded-2xl shadow-xl border border-gray-200 overflow-hidden"
      dir={language === 'ur' ? 'rtl' : 'ltr'}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-md">
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900">{t('chatInterface.title')}</h2>
            <p className="text-xs text-gray-500">{t('chatInterface.poweredBy')}</p>
          </div>
        </div>

        {/* Language Switcher and New Conversation Button */}
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <button
            onClick={handleNewConversation}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={t('chatInterface.newChat')}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            {t('chatInterface.newChat')}
          </button>
        </div>
      </div>

      {/* Messages */}
      <MessageList
        messages={messages}
        streamingMessage={streamingMessage}
        isLoading={isLoading}
      />

      {/* Input */}
      <MessageInput
        onSend={handleSendMessage}
        disabled={isLoading}
        placeholder={t('chatInterface.placeholder')}
      />
    </div>
  )
}
