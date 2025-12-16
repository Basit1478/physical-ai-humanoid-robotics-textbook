import React, { useState, useEffect, useRef } from 'react';
import './Chatbot.css';
import ChatbotAPIService from './ChatbotAPIService';

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Function to get selected text from the page
  const getSelectedText = () => {
    const selectedText = window.getSelection()?.toString().trim() || '';
    return selectedText;
  };

  // Function to handle text selection on the page
  useEffect(() => {
    const handleSelection = () => {
      const text = getSelectedText();
      if (text) {
        setSelectedText(text);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', handleSelection);
    };
  }, []);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() && !selectedText) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: inputValue || selectedText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setSelectedText(''); // Clear selected text after sending
    setIsLoading(true);

    try {
      // Use the API service to send the message
      const response = await ChatbotAPIService.sendMessage({
        query_text: inputValue || selectedText,
        selected_text: selectedText || null,
      });

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: response.answer || 'Sorry, I could not understand your query.',
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, there was an error processing your request. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
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
    <div className="chatbot-container">
      {/* Chatbot widget toggle button */}
      {!isOpen && (
        <button className="chatbot-toggle-button" onClick={toggleChat}>
          💬 Ask AI
        </button>
      )}

      {/* Chatbot widget */}
      {isOpen && (
        <div className="chatbot-widget">
          <div className="chatbot-header">
            <h3>AI Assistant</h3>
            <button className="chatbot-close-button" onClick={toggleChat}>
              ×
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.length === 0 ? (
              <div className="chatbot-welcome-message">
                <p>Hello! I'm your AI assistant. Select text on the page or type a question to get started.</p>
                {selectedText && (
                  <div className="selected-text-preview">
                    <p><strong>Selected text:</strong> "{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}"</p>
                  </div>
                )}
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`chatbot-message ${message.sender}-message`}
                >
                  <div className="message-content">
                    {message.text}
                  </div>
                  <div className="message-timestamp">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="chatbot-message bot-message">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chatbot-input-area">
            {selectedText && (
              <div className="selected-text-indicator">
                Using selected text: "{selectedText.substring(0, 50)}{selectedText.length > 50 ? '...' : ''}"
              </div>
            )}
            <div className="chatbot-input-container">
              <input
                type="text"
                value={inputValue}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder={selectedText ? "Ask about selected text..." : "Type your question..."}
                className="chatbot-input"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || (!inputValue.trim() && !selectedText)}
                className="chatbot-send-button"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;