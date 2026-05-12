'use client';

import { useTranslation } from 'react-i18next';
import { useState } from 'react';

export default function I18nTestPage() {
  const { t, i18n } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language);

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    setCurrentLanguage(lng);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">i18n Test Page</h1>

        <div className="mb-6 flex gap-4">
          <button
            onClick={() => changeLanguage('en')}
            className={`px-4 py-2 rounded-lg ${
              currentLanguage === 'en'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            English
          </button>
          <button
            onClick={() => changeLanguage('ur')}
            className={`px-4 py-2 rounded-lg ${
              currentLanguage === 'ur'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            اردو
          </button>
          <span className="px-4 py-2 bg-gray-100 rounded-lg">
            Current: {currentLanguage}
          </span>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h2 className="font-semibold text-blue-800 mb-2">Chat Interface Translations:</h2>
            <ul className="space-y-1 text-gray-700">
              <li><strong>Title:</strong> {t('chatInterface.title')}</li>
              <li><strong>Powered by:</strong> {t('chatInterface.poweredBy')}</li>
              <li><strong>New Chat:</strong> {t('chatInterface.newChat')}</li>
              <li><strong>Placeholder:</strong> {t('chatInterface.placeholder')}</li>
              <li><strong>Failed to send:</strong> {t('chatInterface.failedToSend')}</li>
              <li><strong>Error processing:</strong> {t('chatInterface.errorProcessing')}</li>
              <li><strong>Started new conversation:</strong> {t('chatInterface.startedNewConversation')}</li>
            </ul>
          </div>

          <div className="p-4 bg-green-50 rounded-lg">
            <h2 className="font-semibold text-green-800 mb-2">Message Input Translations:</h2>
            <ul className="space-y-1 text-gray-700">
              <li><strong>Placeholder:</strong> {t('messageInput.placeholder')}</li>
              <li><strong>Send message:</strong> {t('messageInput.sendMessage')}</li>
              <li><strong>Send:</strong> {t('messageInput.send')}</li>
              <li><strong>Enter to send:</strong> {t('messageInput.enterToSend')}</li>
              <li><strong>Shift+Enter:</strong> {t('messageInput.shiftEnterForNewLine')}</li>
              <li><strong>Click mic:</strong> {t('messageInput.clickMicToSpeak')}</li>
              <li><strong>Listening:</strong> {t('messageInput.listening')}</li>
              <li><strong>Stop recording:</strong> {t('messageInput.stopRecording')}</li>
              <li><strong>Start voice recording:</strong> {t('messageInput.startVoiceRecording')}</li>
              <li><strong>Voice input:</strong> {t('messageInput.voiceInput')}</li>
            </ul>
          </div>

          <div className="p-4 bg-purple-50 rounded-lg">
            <h2 className="font-semibold text-purple-800 mb-2">HTML Direction Test:</h2>
            <p className="text-gray-700">
              The page direction should change based on language. Current direction:
              <span className="font-mono ml-2">{'<html>'} tag has dir="{typeof document !== 'undefined' ? document.documentElement.dir : 'ltr'}"</span>
            </p>
          </div>
        </div>

        <div className="mt-8 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <h3 className="font-semibold text-yellow-800 mb-2">Testing Instructions:</h3>
          <ol className="list-decimal list-inside space-y-1 text-gray-700">
            <li>Click "English" or "اردو" buttons to switch languages</li>
            <li>Observe that all text updates to the selected language</li>
            <li>Check that the HTML direction changes (LTR/RTL)</li>
            <li>Verify that the chat interface components will also update</li>
          </ol>
        </div>
      </div>
    </div>
  );
}