import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import enTranslations from '@/locales/en/translation.json';
import urTranslations from '@/locales/ur/translation.json';

// i18n configuration
const resources = {
  en: {
    translation: enTranslations,
  },
  ur: {
    translation: urTranslations,
  },
};

// Initialize i18n only if not already initialized
if (!i18n.isInitialized) {
  i18n
    .use(LanguageDetector) // Detects user's language
    .use(initReactI18next) // Passes i18n down to react-i18next
    .init({
      resources,
      fallbackLng: 'en', // Default language
      debug: process.env.NODE_ENV === 'development',

      interpolation: {
        escapeValue: false, // React already safes from XSS
      },

      detection: {
        order: ['querystring', 'cookie', 'localStorage', 'sessionStorage', 'navigator'],
        caches: ['localStorage', 'cookie'],
        lookupQuerystring: 'lng',
        lookupCookie: 'i18next',
        lookupLocalStorage: 'i18nextLng',
      },

      // Key separator for nested translations
      keySeparator: '.',

      // Namespace usage (optional)
      ns: ['translation'],
      defaultNS: 'translation',
    });
}

export default i18n;