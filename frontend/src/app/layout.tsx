import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ToastProvider } from '@/lib/contexts/ToastContext'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'Hackathon Todo',
  description: 'Full-stack task management application with authentication',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-gray-50 antialiased">
        <ToastProvider>
          <main className="min-h-screen">{children}</main>
        </ToastProvider>
      </body>
    </html>
  )
}
