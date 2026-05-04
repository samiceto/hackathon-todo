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

  useEffect(() => {
    const currentUser = authClient.getCurrentUser()
    if (!currentUser) { router.push('/signin'); return }
    setUser(currentUser)
    setIsLoading(false)
  }, [router])

  const handleLogout = async () => { await authClient.signout(); router.push('/') }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loading message="Loading chat…" size="large" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="flex-shrink-0 bg-white border-b border-gray-200 px-4 md:px-8">
        <div className="flex items-center gap-3 h-14 max-w-5xl mx-auto">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-teal-600 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-gray-900 hidden sm:block">AI Chat</span>
          </div>

          <div className="flex-1" />

          {/* Tasks link */}
          <Link href="/tasks"
            className="flex items-center gap-1.5 h-8 px-3 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors font-medium">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <span className="hidden sm:inline">Tasks</span>
          </Link>

          {/* User + logout */}
          {user && (
            <div className="flex items-center gap-2">
              <span className="hidden sm:block text-xs text-gray-500">{user.email}</span>
              <button onClick={handleLogout} aria-label="Sign out"
                className="h-8 px-3 flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="hidden sm:inline">Sign out</span>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 flex overflow-hidden px-4 md:px-8 py-6">
        <div className="flex gap-6 w-full max-w-5xl mx-auto">
          {/* Chat - main column */}
          <div className="flex-1 min-w-0 bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden flex flex-col" style={{ height: 'calc(100vh - 8rem)' }}>
            <ChatInterface />
          </div>

          {/* Tips sidebar */}
          <aside className="hidden lg:flex flex-col gap-4 w-64 flex-shrink-0">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">How to use</h3>
              <p className="text-xs text-gray-500 mb-3 leading-relaxed">
                Ask me to help manage your tasks using natural language.
              </p>
              <div className="space-y-1.5">
                {[
                  'Add a task to buy groceries',
                  'Show me all my tasks',
                  'Mark task 5 as complete',
                  'Delete completed tasks',
                ].map((tip) => (
                  <p key={tip} className="text-xs text-gray-600 flex items-start gap-1.5">
                    <span className="text-teal-500 mt-0.5 flex-shrink-0">•</span>
                    <span>"{tip}"</span>
                  </p>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">AI Features</h3>
              <div className="space-y-3">
                {[
                  { icon: '✦', label: 'Natural language', desc: 'No commands needed' },
                  { icon: '⟳', label: 'Real-time', desc: 'Instant streaming responses' },
                  { icon: '◎', label: 'Context aware', desc: 'Remembers conversation' },
                ].map(({ icon, label, desc }) => (
                  <div key={label} className="flex items-start gap-2.5">
                    <span className="text-teal-500 text-sm mt-0.5 w-4 flex-shrink-0">{icon}</span>
                    <div>
                      <p className="text-xs font-medium text-gray-800">{label}</p>
                      <p className="text-xs text-gray-500">{desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  )
}
