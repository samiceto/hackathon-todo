/**
 * MessageList Component
 *
 * Scrollable list of chat messages with auto-scroll to bottom.
 */

import { useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'
import { ChatMessage as ChatMessageType } from '@/lib/api/chatkit'

interface MessageListProps {
  messages: ChatMessageType[]
  streamingMessage?: string
  isLoading?: boolean
}

export default function MessageList({
  messages,
  streamingMessage,
  isLoading = false,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, streamingMessage])

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-4 py-6 space-y-4 scroll-smooth"
    >
      {messages.length === 0 && !streamingMessage && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
            <svg
              className="w-8 h-8 text-primary-600"
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
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Start a Conversation
          </h3>
          <p className="text-sm text-gray-600 max-w-sm">
            Ask me to help you manage your tasks! Try asking me to add a task, view your
            tasks, or mark something as complete.
          </p>

          {/* Suggested Prompts */}
          <div className="mt-6 space-y-2">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Try asking:
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              <span className="px-3 py-1 bg-white border border-gray-200 rounded-full text-xs text-gray-700">
                "Add a task to buy groceries"
              </span>
              <span className="px-3 py-1 bg-white border border-gray-200 rounded-full text-xs text-gray-700">
                "Show me all my tasks"
              </span>
              <span className="px-3 py-1 bg-white border border-gray-200 rounded-full text-xs text-gray-700">
                "Mark task 5 as complete"
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Render messages */}
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
        />
      ))}

      {/* Streaming message */}
      {streamingMessage && (
        <ChatMessage
          role="assistant"
          content={streamingMessage}
          isStreaming={true}
        />
      )}

      {/* Loading indicator */}
      {isLoading && !streamingMessage && (
        <div className="flex gap-3">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
            <svg
              className="w-5 h-5 text-gray-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <div className="flex items-center gap-1 px-4 py-3 rounded-2xl rounded-tl-sm bg-white border border-gray-200 shadow-sm">
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
          </div>
        </div>
      )}
    </div>
  )
}
