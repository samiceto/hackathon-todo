import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
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
    <html lang="en" className={`${inter.variable} antialiased`}>
      <body className="min-h-screen bg-gray-50">
        <Providers>
          <main className="min-h-screen">{children}</main>
        </Providers>
      </body>
    </html>
  )
}
