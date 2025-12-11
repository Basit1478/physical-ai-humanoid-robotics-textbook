import React, { useState } from 'react';
import clsx from 'clsx';
import styles from './CustomFeatures.module.css';
import { translateApi } from '@site/src/api';

const UrduButton = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [translatedText, setTranslatedText] = useState('');
  const [error, setError] = useState('');

  const handleTranslate = async () => {
    // Get selected text
    const selectedText = window.getSelection().toString();

    if (!selectedText) {
      setError('Please select some text to translate to Urdu');
      setTimeout(() => setError(''), 3000);
      return;
    }

    setIsLoading(true);
    setTranslatedText('');
    setError('');

    try {
      // Call the backend translation API - using a default chapter ID since this is for selected text
      const response = await translateApi.translateChapter(selectedText, 'selected-text');

      if (response.translated_content) {
        setTranslatedText(response.translated_content);
      } else {
        setError('Translation completed but no content returned. The AI service may be warming up.');
      }
    } catch (error) {
      console.error('Translation error:', error);
      setError('⚠️ Unable to connect to translation service. The backend may be starting up (30-60s on free tier). Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.customFeature}>
      <h3>Urdu Translation</h3>
      <p>Select any text on the page and click the button below to translate it to Urdu:</p>

      <button
        onClick={handleTranslate}
        disabled={isLoading}
        className={clsx('button button--primary', styles.customButton)}
      >
        {isLoading ? 'Translating...' : 'Translate to Urdu'}
      </button>

      {error && (
        <div style={{
          marginTop: '10px',
          padding: '10px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px',
          color: '#856404'
        }}>
          {error}
        </div>
      )}

      {translatedText && (
        <div className={styles.translationResult}>
          <h4>Translated Text (Urdu):</h4>
          <p style={{ direction: 'rtl', textAlign: 'right', fontSize: '16px' }}>{translatedText}</p>
        </div>
      )}

      <p><small>Powered by Gemini AI for accurate Urdu translations.</small></p>
    </div>
  );
};

export default UrduButton;