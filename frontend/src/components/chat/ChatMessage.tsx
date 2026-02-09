/**
 * ChatMessage Component
 *
 * Displays a single chat message with role-based styling.
 */

interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
  isStreaming?: boolean
}

export default function ChatMessage({
  role,
  content,
  timestamp,
  isStreaming = false,
}: ChatMessageProps) {
  const isUser = role === 'user'

  return (
    <div
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} animate-slide-up`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-600' : 'bg-gray-300'
        }`}
      >
        {isUser ? (
          <svg
            className="w-5 h-5 text-white"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
        ) : (
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
        )}
      </div>

      {/* Message Bubble */}
      <div className={`flex flex-col gap-1 max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-2 rounded-2xl ${
            isUser
              ? 'bg-primary-600 text-white rounded-tr-sm'
              : 'bg-white border border-gray-200 text-gray-900 rounded-tl-sm shadow-sm'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap break-words">{content}</p>

          {/* Streaming indicator */}
          {isStreaming && !isUser && (
            <div className="flex gap-1 mt-2">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
            </div>
          )}
        </div>

        {/* Timestamp */}
        {timestamp && (
          <span className="text-xs text-gray-500 px-2">
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>
    </div>
  )
}
