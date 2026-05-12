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

interface ChatInterfaceProps {
  onClose?: () => void
}

export default function ChatInterface({ onClose }: ChatInterfaceProps) {
  const { t } = useTranslation()
  const { language } = useI18n()
  const router = useRouter()
  const toast = useToast()

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streamingMessage, setStreamingMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<number | undefined>(undefined)

  useEffect(() => {
    const user = authClient.getCurrentUser()
    if (!user) router.push('/signin')
  }, [router])

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMessage: ChatMessage = { role: 'user', content: text, timestamp: new Date() }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    setStreamingMessage('')

    try {
      let fullResponse = ''
      for await (const chunk of chatkitApi.streamResponse(text, conversationId, language, setConversationId)) {
        fullResponse += chunk
        setStreamingMessage(fullResponse)
      }
      if (fullResponse) {
        setMessages((prev) => [...prev, { role: 'assistant', content: fullResponse, timestamp: new Date() }])
      }
      setStreamingMessage('')
    } catch (error: any) {
      console.error(t('chatInterface.errorProcessing'), error)
      toast.error(error.message || t('chatInterface.failedToSend'))
      setMessages((prev) => [...prev, { role: 'assistant', content: t('chatInterface.errorProcessing'), timestamp: new Date() }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewConversation = () => {
    setMessages([])
    setConversationId(undefined)
    setStreamingMessage('')
    toast.success(t('chatInterface.startedNewConversation'))
  }

  return (
    <div className="flex flex-col h-full bg-white" dir={language === 'ur' ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2.5 border-b border-gray-100 flex-shrink-0">
        <div className="w-7 h-7 bg-teal-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-gray-900 leading-none">{t('chatInterface.title')}</p>
          <p className="text-[11px] text-gray-400 mt-0.5">{t('chatInterface.poweredBy')}</p>
        </div>
        <div className="flex items-center gap-1">
          <LanguageSwitcher />
          <button
            onClick={handleNewConversation}
            disabled={isLoading}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all disabled:opacity-40"
            title={t('chatInterface.newChat')}
            aria-label={t('chatInterface.newChat')}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all"
              aria-label="Close chat"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <MessageList
        messages={messages}
        streamingMessage={streamingMessage}
        isLoading={isLoading}
        onSuggestion={handleSendMessage}
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
