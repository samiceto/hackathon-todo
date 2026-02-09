/**
 * Chat Page
 *
 * AI-powered chat interface for conversational task management.
 * Users can add, view, update, and manage tasks through natural language.
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import authClient from '@/lib/auth/auth-client'
import ChatInterface from '@/components/chat/ChatInterface'
import Loading from '@/components/ui/Loading'

export default function ChatPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState<{ id: number; email: string } | null>(null)

  // Check authentication on mount
  useEffect(() => {
    const currentUser = authClient.getCurrentUser()
    if (!currentUser) {
      router.push('/signin')
      return
    }

    setUser(currentUser)
    setIsLoading(false)
  }, [router])

  // Handle logout
  const handleLogout = async () => {
    await authClient.signout()
    router.push('/')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading message="Loading chat..." size="large" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/20">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200 sticky top-0 z-40 backdrop-blur-sm bg-white/90">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo/Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
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
                <h1 className="text-xl font-bold text-gray-900">AI Chat</h1>
                {user && <p className="text-xs text-gray-500">{user.email}</p>}
              </div>
            </div>

            {/* Navigation & Actions */}
            <div className="flex items-center gap-3">
              {/* Tasks Link */}
              <Link
                href="/tasks"
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-colors font-medium focus:outline-none focus:ring-4 focus:ring-gray-200"
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
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  />
                </svg>
                Tasks
              </Link>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-colors font-medium focus:outline-none focus:ring-4 focus:ring-gray-200"
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
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface - Main Column */}
          <div className="lg:col-span-2">
            <div className="h-[calc(100vh-12rem)]">
              <ChatInterface />
            </div>
          </div>

          {/* Sidebar - Tips & Info */}
          <div className="lg:col-span-1 space-y-6">
            {/* Welcome Card */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                  <svg
                    className="w-6 h-6 text-primary-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900">How to Use</h3>
              </div>

              <div className="space-y-3 text-sm text-gray-600">
                <p>
                  Chat with the AI assistant to manage your tasks using natural language.
                </p>

                <div className="space-y-2">
                  <p className="font-semibold text-gray-900">Try asking:</p>
                  <ul className="space-y-1 pl-4">
                    <li className="flex items-start gap-2">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>"Add a task to buy groceries"</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>"Show me all my tasks"</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>"Mark task 5 as complete"</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>"Update task 3's description"</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>"Delete completed tasks"</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Features Card */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">AI Features</h3>

              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-4 h-4 text-green-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">Natural Language</p>
                    <p className="text-xs text-gray-600">
                      Talk naturally, no commands needed
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-4 h-4 text-blue-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">Real-time Responses</p>
                    <p className="text-xs text-gray-600">
                      Instant feedback on task operations
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-4 h-4 text-purple-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">Context Aware</p>
                    <p className="text-xs text-gray-600">
                      Remembers your conversation history
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
