import React, { useState } from 'react';
import clsx from 'clsx';
import styles from './CustomFeatures.module.css';
import { translateApi } from '@site/src/api';

const UrduButton = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [translatedText, setTranslatedText] = useState('');

  const handleTranslate = async () => {
    // Get selected text
    const selectedText = window.getSelection().toString();

    if (!selectedText) {
      alert('Please select some text to translate to Urdu');
      return;
    }

    setIsLoading(true);
    setTranslatedText('');

    try {
      // Call the backend translation API
      const response = await translateApi.translate(selectedText, 'en', 'ur');
      setTranslatedText(response.translated_text);
      alert('Text translated to Urdu successfully!');
    } catch (error) {
      console.error('Translation error:', error);
      alert('Failed to translate text. Please try again.');
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
        {isLoading ? 'Translating...' : '-translate to Urdu'}
      </button>

      {translatedText && (
        <div className={styles.translationResult}>
          <h4>Translated Text:</h4>
          <p style={{ direction: 'rtl', textAlign: 'right' }}>{translatedText}</p>
        </div>
      )}

      <p><small>Powered by Gemini AI for accurate Urdu translations.</small></p>
    </div>
  );
};

export default UrduButton;