import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-teal-50/60 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Ambient blobs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-teal-200/30 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-teal-300/20 rounded-full blur-3xl pointer-events-none" />
      {/* Subtle dot grid */}
      <div className="absolute inset-0 bg-[radial-gradient(#0d948820_1px,transparent_1px)] bg-[size:28px_28px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-sm">
        {/* Logo + Brand */}
        <div className="text-center mb-10 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-teal-600 shadow-xl shadow-teal-600/30 mb-5 ring-4 ring-teal-100">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <h1 className="text-3xl font-extrabold text-teal-900 mb-2 tracking-tight">TaskFlow</h1>
          <p className="text-teal-700/70 text-base font-medium">Manage tasks smarter with AI assistance</p>
        </div>

        {/* Feature pills */}
        <div className="mb-8 space-y-2 animate-slide-up">
          {[
            { label: 'Priority, tags, due dates & recurrence' },
            { label: 'AI-powered natural language chat' },
            { label: 'Smart reminders & notifications' },
          ].map(({ label }) => (
            <div key={label} className="flex items-center gap-3 px-4 py-2.5 bg-white/80 border border-teal-100 rounded-xl shadow-sm text-sm text-teal-800">
              <span className="flex-shrink-0 w-4 h-4 rounded-full bg-teal-600 flex items-center justify-center">
                <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </span>
              <span className="font-medium">{label}</span>
            </div>
          ))}
        </div>

        {/* CTA buttons */}
        <div className="space-y-3 animate-slide-up">
          <Link
            href="/signup"
            className="flex items-center justify-center w-full px-6 py-3.5 bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-white font-bold rounded-xl shadow-lg shadow-orange-500/30 transition-all duration-150 hover:-translate-y-px hover:shadow-orange-500/40 cursor-pointer"
          >
            Get started free
          </Link>
          <Link
            href="/signin"
            className="flex items-center justify-center w-full px-6 py-3.5 bg-white hover:bg-teal-50 border border-teal-200 text-teal-700 font-semibold rounded-xl transition-all duration-150 hover:-translate-y-px shadow-sm cursor-pointer"
          >
            Sign in to your account
          </Link>
        </div>

        <p className="text-center text-xs text-teal-500/70 mt-6 font-medium">No credit card required · Free forever</p>
      </div>
    </div>
  )
}
