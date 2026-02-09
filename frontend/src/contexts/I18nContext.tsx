'use client';

import { createContext, useContext, useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import i18nInstance from '@/lib/i18n/config';

interface I18nContextType {
  language: string;
  changeLanguage: (lng: string) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (context === undefined) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};

interface I18nProviderProps {
  children: React.ReactNode;
}

export const I18nProvider = ({ children }: I18nProviderProps) => {
  // Ensure i18n is initialized before using hooks
  const { i18n, t } = useTranslation();
  const [language, setLanguage] = useState(i18nInstance.language || 'en');
  const [isReady, setIsReady] = useState(i18nInstance.isInitialized);

  const changeLanguage = (lng: string) => {
    if (typeof i18n.changeLanguage === 'function') {
      i18n.changeLanguage(lng);
    }
    localStorage.setItem('i18nextLng', lng);
    document.documentElement.lang = lng;

    // Update the local state to trigger re-render
    setLanguage(lng);
  };

  useEffect(() => {
    // Initialize language detection after ensuring i18n is ready
    const initializeLanguage = () => {
      const detectedLang = localStorage.getItem('i18nextLng') || 'en';
      if (i18nInstance.isInitialized) {
        i18nInstance.changeLanguage(detectedLang).then(() => {
          setLanguage(detectedLang);
          setIsReady(true);

          // Set HTML lang attribute for accessibility
          document.documentElement.lang = detectedLang;
        });
      }
    };

    // Set up event listener to sync state with i18n instance
    const handleLanguageChange = (lng: string) => {
      setLanguage(lng);
    };

    if (i18nInstance.isInitialized) {
      initializeLanguage();
    } else {
      // Use event-based initialization instead of polling
      const handleInitialized = () => {
        initializeLanguage();
      };
      if (typeof i18nInstance.on === 'function') {
        i18nInstance.on('initialized', handleInitialized);
      }
    }

    if (typeof i18nInstance.on === 'function') {
      i18nInstance.on('languageChanged', handleLanguageChange);
    }

    // Cleanup event listeners
    return () => {
      if (typeof i18nInstance.off === 'function') {
        i18nInstance.off('languageChanged', handleLanguageChange);
      }
    };
  }, []); // Run only once on mount

  const contextValue = useMemo(() => ({
    language,
    changeLanguage,
    t,
  }), [language, changeLanguage, t]);

  // Don't render children until i18n is ready
  if (!isReady) {
    return null;
  }

  return (
    <I18nContext.Provider value={contextValue}>
      {children}
    </I18nContext.Provider>
  );
};