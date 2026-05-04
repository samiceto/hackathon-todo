import SignupForm from '@/components/auth/SignupForm'
import Link from 'next/link'

export const metadata = {
  title: 'Create Account — TaskFlow',
  description: 'Create your account to start managing tasks',
}

export default function SignupPage() {
  return (
    <div className="min-h-screen bg-teal-50 flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-teal-900 via-teal-800 to-teal-700 relative overflow-hidden flex-col justify-between p-12">
        <div className="absolute inset-0 bg-[radial-gradient(#ffffff08_1px,transparent_1px)] bg-[size:32px_32px]" />
        <div className="absolute top-0 right-0 w-72 h-72 bg-teal-600/30 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-teal-950/50 rounded-full blur-3xl" />

        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/15 rounded-xl flex items-center justify-center backdrop-blur-sm ring-1 ring-white/20">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span className="text-white font-bold text-xl tracking-tight">TaskFlow</span>
          </div>
        </div>

        <div className="relative z-10 space-y-8">
          {[
            { title: 'AI-powered chat', desc: 'Manage tasks via natural language' },
            { title: 'Smart scheduling', desc: 'Recurrence rules & reminders' },
            { title: 'Full-featured', desc: 'Priority, tags, due dates & more' },
          ].map((f) => (
            <div key={f.title} className="flex items-start gap-4">
              <div className="w-8 h-8 bg-white/15 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ring-1 ring-white/20">
                <svg className="w-4 h-4 text-teal-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-white font-semibold text-sm">{f.title}</p>
                <p className="text-teal-300 text-xs mt-0.5">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="relative z-10 flex items-center gap-2">
          <div className="h-1 w-2 bg-white/30 rounded-full" />
          <div className="h-1 w-8 bg-white rounded-full" />
          <div className="h-1 w-2 bg-white/30 rounded-full" />
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-white">
        <div className="w-full max-w-sm animate-fade-in">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center shadow-md shadow-teal-600/30">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span className="font-bold text-teal-900 text-lg tracking-tight">TaskFlow</span>
          </div>

          <div className="mb-8">
            <h1 className="text-2xl font-extrabold text-teal-900 mb-1 tracking-tight">Create your account</h1>
            <p className="text-teal-600/70 text-sm font-medium">Get started for free — no card needed</p>
          </div>

          <SignupForm />

          <p className="text-center text-xs text-teal-400/70 mt-6">
            By creating an account you agree to our{' '}
            <span className="text-teal-500">Terms of Service</span>
          </p>

          <p className="text-center text-xs text-teal-400 mt-4">
            <Link href="/" className="hover:text-teal-600 transition-colors font-medium">← Back to home</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
