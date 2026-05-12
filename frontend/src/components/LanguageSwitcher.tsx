'use client';

import { useI18n } from '@/contexts/I18nContext';
import { useState, useEffect } from 'react';

const LanguageSwitcher = () => {
  const { language, changeLanguage } = useI18n();
  const [mounted, setMounted] = useState(false);

  // Set mounted to true on client side to avoid hydration issues
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Render nothing on the server to avoid hydration mismatch
    return null;
  }

  const toggleLanguage = () => {
    const newLanguage = language === 'en' ? 'ur' : 'en';
    changeLanguage(newLanguage);
  };

  return (
    <button
      onClick={toggleLanguage}
      className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
      aria-label={`Switch to ${language === 'en' ? 'Urdu' : 'English'}`}
    >
      {language === 'en' ? 'اردو' : 'English'}
    </button>
  );
};

export default LanguageSwitcher;