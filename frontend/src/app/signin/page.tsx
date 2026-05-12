import SigninForm from '@/components/auth/SigninForm'
import Link from 'next/link'

export const metadata = {
  title: 'Sign In — TaskFlow',
  description: 'Sign in to your account',
}

export default function SigninPage() {
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

        <div className="relative z-10 space-y-6">
          <blockquote className="text-white/90 text-2xl font-light leading-relaxed">
            "The secret of getting ahead is getting started."
          </blockquote>
          <p className="text-teal-300 text-sm font-medium">— Mark Twain</p>
        </div>

        <div className="relative z-10 flex items-center gap-2">
          <div className="h-1 w-8 bg-white rounded-full" />
          <div className="h-1 w-2 bg-white/30 rounded-full" />
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
            <h1 className="text-2xl font-extrabold text-teal-900 mb-1 tracking-tight">Welcome back</h1>
            <p className="text-teal-600/70 text-sm font-medium">Sign in to continue to your tasks</p>
          </div>

          <SigninForm />

          <p className="text-center text-xs text-teal-400 mt-8">
            <Link href="/" className="hover:text-teal-600 transition-colors font-medium">← Back to home</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
