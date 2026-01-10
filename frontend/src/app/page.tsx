import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8 text-center">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">
            Hackathon Todo
          </h1>
          <p className="text-lg text-gray-600">
            Manage your tasks efficiently
          </p>
        </div>

        <div className="space-y-4">
          <Link
            href="/signup"
            className="block w-full rounded-lg bg-primary-600 px-4 py-3 text-center font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
          >
            Get Started
          </Link>

          <Link
            href="/signin"
            className="block w-full rounded-lg border border-gray-300 px-4 py-3 text-center font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
          >
            Sign In
          </Link>
        </div>

        <p className="text-sm text-gray-500">
          Step 2: Full-Stack Web Application
        </p>
      </div>
    </div>
  )
}
