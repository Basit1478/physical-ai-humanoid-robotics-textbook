import React, { useState } from 'react';
import clsx from 'clsx';
import styles from './CustomFeatures.module.css';
import { ragApi } from '@site/src/api';

const RagChatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      content: 'Hello! I\'m your AI assistant for the Physical AI & Humanoid Robotics textbook. Ask me anything about the content!'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      sender: 'user',
      content: inputValue
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the backend RAG API
      const response = await ragApi.chat(inputValue);
      const aiResponse = {
        id: messages.length + 2,
        sender: 'ai',
        content: response.answer || 'I received your question but couldn\'t generate a response. Please try again.'
      };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: messages.length + 2,
        sender: 'ai',
        content: 'Sorry, I encountered an error processing your request. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={styles.customFeature}>
      <h3>AI Assistant (RAG Chatbot)</h3>
      <p>Ask questions about the Physical AI & Humanoid Robotics textbook content:</p>

      <div className={styles.chatContainer}>
        <div className={styles.chatMessages}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={clsx(
                styles.message,
                message.sender === 'user' ? styles.userMessage : styles.aiMessage
              )}
            >
              <strong>{message.sender === 'user' ? 'You: ' : 'AI Assistant: '}</strong>
              {message.content}
            </div>
          ))}
          {isLoading && (
            <div className={clsx(styles.message, styles.aiMessage)}>
              <strong>AI Assistant: </strong>
              <span className={styles.typingIndicator}>Thinking...</span>
            </div>
          )}
        </div>

        <div className={styles.chatInputArea}>
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about the textbook content..."
            className={styles.chatInput}
            rows={2}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="button button--primary"
          >
            Send
          </button>
        </div>
      </div>

      <p><small>Powered by RAG (Retrieval Augmented Generation) with Qdrant vector database and Gemini AI.</small></p>
    </div>
  );
};

export default RagChatbot;