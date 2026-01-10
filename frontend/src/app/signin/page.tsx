import SigninForm from '@/components/auth/SigninForm'
import Link from 'next/link'

export const metadata = {
  title: 'Sign In - Hackathon Todo',
  description: 'Sign in to your account to manage your tasks',
}

export default function SigninPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-gray-50 via-white to-primary-50/30 relative overflow-hidden">
      {/* Decorative Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary-100/40 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-primary-200/30 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
      </div>

      {/* Main Content */}
      <div className="w-full max-w-md relative z-10">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <Link
            href="/"
            className="inline-block mb-6 group"
          >
            <div className="flex items-center justify-center gap-2 text-primary-600 hover:text-primary-700 transition-colors">
              <svg
                className="w-8 h-8 transform group-hover:-translate-x-1 transition-transform"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              <span className="font-semibold">Back to home</span>
            </div>
          </Link>

          <h1 className="text-4xl font-bold text-gray-900 mb-3 tracking-tight">
            Welcome back
          </h1>
          <p className="text-gray-600 text-lg">
            Sign in to continue managing your tasks
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-200/50 p-8 animate-slide-up">
          <SigninForm />
        </div>

        {/* Footer Note */}
        <p className="text-center text-xs text-gray-500 mt-6 animate-fade-in">
          Protected by industry-standard encryption
        </p>
      </div>
    </div>
  )
}
