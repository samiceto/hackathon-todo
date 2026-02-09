'use client'

import { ToastProvider } from '@/lib/contexts/ToastContext'
import { I18nProvider } from '@/contexts/I18nContext'
import '@/lib/i18n/config'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <I18nProvider>
      <ToastProvider>
        {children}
      </ToastProvider>
    </I18nProvider>
  )
}
