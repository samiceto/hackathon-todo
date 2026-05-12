import { useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'
import { ChatMessage as ChatMessageType } from '@/lib/api/chatkit'

const SUGGESTIONS = [
  '"Add a task to buy groceries"',
  '"Show me all my tasks"',
  '"Mark task 5 as complete"',
  '"Delete completed tasks"',
]

interface MessageListProps {
  messages: ChatMessageType[]
  streamingMessage?: string
  isLoading?: boolean
  onSuggestion?: (text: string) => void
}

export default function MessageList({ messages, streamingMessage, isLoading = false, onSuggestion }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, streamingMessage])

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3 scroll-smooth">
      {messages.length === 0 && !streamingMessage && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center py-8">
          <div className="w-12 h-12 bg-teal-50 rounded-2xl flex items-center justify-center mb-3">
            <svg className="w-6 h-6 text-teal-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h3 className="text-sm font-semibold text-gray-900 mb-1">AI Task Assistant</h3>
          <p className="text-xs text-gray-500 max-w-[220px] mb-4">
            Ask me to help manage your tasks using natural language.
          </p>
          <div className="space-y-1.5 w-full">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => onSuggestion?.(s.replace(/"/g, ''))}
                className="w-full text-left px-3 py-2 bg-white border border-gray-200 hover:border-teal-300 hover:bg-teal-50 rounded-lg text-xs text-gray-600 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {messages.map((message, index) => (
        <ChatMessage key={index} role={message.role} content={message.content} timestamp={message.timestamp} />
      ))}

      {streamingMessage && (
        <ChatMessage role="assistant" content={streamingMessage} isStreaming={true} />
      )}

      {isLoading && !streamingMessage && (
        <div className="flex gap-2.5">
          <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div className="flex items-center gap-1 px-3 py-2 rounded-2xl rounded-tl-sm bg-white border border-gray-200 shadow-sm">
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      )}
    </div>
  )
}
