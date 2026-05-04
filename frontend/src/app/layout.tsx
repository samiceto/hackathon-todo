import type { Metadata } from 'next'
import { Plus_Jakarta_Sans } from 'next/font/google'
import { Providers } from './providers'
import '../styles/globals.css'

const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-jakarta',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700', '800'],
})

export const metadata: Metadata = {
  title: 'TaskFlow — Smart Task Management',
  description: 'Manage tasks intelligently with AI-powered assistance',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${jakarta.variable}`}>
      <body className="min-h-screen bg-teal-50 antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
