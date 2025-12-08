import React, { useState, useEffect } from 'react';
import { useColorMode } from '@docusaurus/theme-common';

// Modern Dynamic Button Component
const DynamicButton = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  className = '', 
  title = '',
  icon = null,
  ...props 
}) => {
  const { colorMode } = useColorMode();
  const isDarkMode = colorMode === 'dark';
  
  // Define button styles based on variant and size
  const getButtonStyles = () => {
    let baseClasses = 'transition-all duration-200 ease-in-out font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 ';
    
    // Base styles
    baseClasses += 'inline-flex items-center justify-center border-0 ';
    
    // Variant styles with more modern colors
    switch(variant) {
      case 'primary':
        baseClasses += isDarkMode 
          ? 'bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white focus:ring-pink-500 focus:ring-offset-gray-900 ' 
          : 'bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white focus:ring-pink-500 focus:ring-offset-white ';
        break;
      case 'secondary':
        baseClasses += isDarkMode 
          ? 'bg-gray-700 hover:bg-gray-600 text-gray-100 focus:ring-gray-600 focus:ring-offset-gray-900 ' 
          : 'bg-gray-100 hover:bg-gray-200 text-gray-800 focus:ring-gray-400 focus:ring-offset-white ';
        break;
      case 'tertiary':
        baseClasses += isDarkMode 
          ? 'bg-transparent hover:bg-gray-700 text-gray-100 focus:ring-gray-600 focus:ring-offset-gray-900 ' 
          : 'bg-transparent hover:bg-gray-100 text-gray-600 focus:ring-gray-400 focus:ring-offset-white ';
        break;
      case 'icon':
        baseClasses += isDarkMode 
          ? 'bg-transparent hover:bg-gray-700 text-white rounded-full focus:ring-gray-600 focus:ring-offset-gray-900 ' 
          : 'bg-transparent hover:bg-gray-100 text-gray-600 rounded-full focus:ring-gray-400 focus:ring-offset-white ';
        break;
      default:
        baseClasses += isDarkMode 
          ? 'bg-gray-600 hover:bg-gray-500 text-white focus:ring-gray-500 focus:ring-offset-gray-900 ' 
          : 'bg-gray-100 hover:bg-gray-200 text-gray-800 focus:ring-gray-400 focus:ring-offset-white ';
    }
    
    // Size styles
    switch(size) {
      case 'small':
        baseClasses += 'text-xs px-3 py-1.5 min-h-[30px] ';
        break;
      case 'large':
        baseClasses += 'text-lg px-6 py-3 min-h-[48px] ';
        break;
      default:
        baseClasses += 'text-sm px-4 py-2 min-h-[40px] ';
    }
    
    // Disabled state
    if(disabled) {
      baseClasses += 'opacity-50 cursor-not-allowed pointer-events-none ';
    }
    
    // Additional custom classes
    baseClasses += className;
    
    return baseClasses;
  };
  
  return (
    <button
      className={getButtonStyles()}
      onClick={onClick}
      disabled={disabled}
      title={title}
      {...props}
    >
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
};

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: "Hey there! 👋 I'm your AI Robotics Tutor. How can I help you with robotics, AI, or ROS today?", sender: 'bot', timestamp: new Date().toISOString() }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en'); // Default to English
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [showPersonalizationPanel, setShowPersonalizationPanel] = useState(false);
  const [showSettingsPanel, setShowSettingsPanel] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([
    "Explain ROS architecture",
    "How do I start with robotics?",
    "What sensors should I use for navigation?",
    "Best practices for robot control"
  ]);
  const [userInfo, setUserInfo] = useState({
    educationLevel: '',
    fieldOfStudy: '',
    background: ''
  });

  const { colorMode } = useColorMode();
  const isDarkMode = colorMode === 'dark';

  // Toggle chat widget open/close
  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // Handle sending a message
  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Add user message to chat
    const userMessage = { 
      id: Date.now(), 
      text: inputValue, 
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setSuggestedQuestions([]); // Clear suggestions after user sends a message
    const newInputValue = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Call backend API to get response
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: newInputValue,
          session_id: sessionId,
          target_language: selectedLanguage
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update session ID if new session was created
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // Add bot response to chat
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle key press (Enter to send, Shift+Enter for new line)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle suggested question click
  const handleSuggestedQuestion = (question) => {
    setInputValue(question);
    setTimeout(() => {
      handleSend();
    }, 100);
  };

  // Handle language change
  const handleLanguageChange = (langCode) => {
    setSelectedLanguage(langCode);
    setShowLanguageSelector(false);
  };

  // Handle personalization update
  const handlePersonalizationSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:8000/api/personalization/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        body: JSON.stringify(userInfo)
      });

      if (response.ok) {
        alert('Profile updated successfully!');
        setShowPersonalizationPanel(false);
      } else {
        alert('Error updating profile');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Error updating profile');
    }
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Component for language selector
  const LanguageSelector = () => (
    <div className={`relative ${isDarkMode ? 'dark' : ''}`}>
      <DynamicButton
        variant="tertiary"
        size="small"
        onClick={() => setShowLanguageSelector(!showLanguageSelector)}
        className="flex items-center gap-1"
      >
        <span className="text-lg">{selectedLanguage.toUpperCase()}</span>
        <svg width="12" height="8" viewBox="0 0 12 8" fill="currentColor" className="ml-1">
          <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </DynamicButton>
      {showLanguageSelector && (
        <div className={`absolute right-0 mt-1 w-32 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 ${isDarkMode ? 'dark' : ''}`}>
          {[
            { code: 'en', name: 'English' },
            { code: 'ur', name: 'Urdu' },
            { code: 'es', name: 'Spanish' },
            { code: 'fr', name: 'French' }
          ].map(lang => (
            <DynamicButton
              key={lang.code}
              variant={selectedLanguage === lang.code ? 'primary' : 'tertiary'}
              size="small"
              onClick={() => handleLanguageChange(lang.code)}
              className={`w-full justify-start ${selectedLanguage === lang.code ? 'bg-blue-100 dark:bg-blue-900' : ''}`}
            >
              {lang.name}
            </DynamicButton>
          ))}
        </div>
      )}
    </div>
  );

  // Component for settings panel
  const SettingsPanel = () => (
    <div className={`absolute right-full top-0 mr-2 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl p-4 z-40 ${isDarkMode ? 'dark' : ''}`}>
      <h3 className="font-semibold mb-3 text-gray-800 dark:text-white">Settings</h3>
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-300">Theme</label>
          <select
            value={colorMode}
            onChange={(e) => {}}
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-300">Language</label>
          <LanguageSelector />
        </div>
      </div>
      <DynamicButton 
        variant="secondary" 
        size="small" 
        className="mt-3 w-full"
        onClick={() => setShowSettingsPanel(false)}
      >
        Close
      </DynamicButton>
    </div>
  );

  // Component for personalization panel
  const PersonalizationPanel = () => (
    <div className={`absolute right-full top-0 mr-2 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl p-4 z-40 ${isDarkMode ? 'dark' : ''}`}>
      <h3 className="font-semibold mb-3 text-gray-800 dark:text-white">Personalize Learning</h3>
      <form onSubmit={handlePersonalizationSubmit}>
        <div className="mb-3">
          <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-300">Education Level:</label>
          <select
            value={userInfo.educationLevel}
            onChange={(e) => setUserInfo({...userInfo, educationLevel: e.target.value})}
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Select level</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-300">Field of Study:</label>
          <input
            type="text"
            value={userInfo.fieldOfStudy}
            onChange={(e) => setUserInfo({...userInfo, fieldOfStudy: e.target.value})}
            placeholder="e.g., Computer Science"
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        <div className="mb-3">
          <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-300">Background:</label>
          <textarea
            value={userInfo.background}
            onChange={(e) => setUserInfo({...userInfo, background: e.target.value})}
            placeholder="Tell us about your background..."
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            rows={2}
          />
        </div>
        <div className="flex gap-2 mt-4">
          <DynamicButton 
            type="submit" 
            variant="primary"
            size="small"
            className="flex-1"
          >
            Save
          </DynamicButton>
          <DynamicButton 
            type="button" 
            variant="secondary"
            size="small"
            onClick={() => setShowPersonalizationPanel(false)}
          >
            Cancel
          </DynamicButton>
        </div>
      </form>
    </div>
  );

  return (
    <div className={`chat-widget ${isOpen ? 'open' : ''} ${isDarkMode ? 'dark' : ''} fixed right-6 bottom-6 z-[9999]`}>
      {/* Floating button */}
      {!isOpen && (
        <DynamicButton 
          variant="primary" 
          size="large"
          onClick={toggleChat}
          className="shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 rounded-full w-16 h-16 flex items-center justify-center text-lg"
          icon="🤖"
        >
          <span className="sr-only">Open Chat</span>
        </DynamicButton>
      )}

      {/* Chat window */}
      {isOpen && (
        <div className={`chat-window w-96 h-[580px] flex flex-col bg-gradient-to-br from-pink-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 border border-pink-100 dark:border-gray-700 rounded-3xl shadow-2xl overflow-hidden ${isDarkMode ? 'dark' : ''}`}>
          {/* Header */}
          <div className="chat-header bg-gradient-to-r from-pink-500 to-purple-600 text-white p-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <div>
                <h3 className="font-bold text-lg">AI Robotics Tutor</h3>
                <p className="text-xs opacity-80">Always learning, always helping</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <DynamicButton
                variant="tertiary"
                size="small"
                onClick={() => setShowPersonalizationPanel(!showPersonalizationPanel)}
                title="Personalize your learning experience"
                className="text-white hover:text-white"
              >
                👤
              </DynamicButton>
              <DynamicButton
                variant="tertiary"
                size="small"
                onClick={() => setShowSettingsPanel(!showSettingsPanel)}
                title="Settings"
                className="text-white hover:text-white"
              >
                ⚙️
              </DynamicButton>
              <DynamicButton 
                variant="tertiary"
                size="small"
                onClick={toggleChat}
                className="text-white hover:text-white"
              >
                ×
              </DynamicButton>
            </div>
          </div>

          {/* Panels */}
          {(showPersonalizationPanel || showSettingsPanel) && (
            <div className="absolute top-14 right-96 z-50">
              {showPersonalizationPanel && <PersonalizationPanel />}
              {showSettingsPanel && <SettingsPanel />}
            </div>
          )}

          {/* Messages */}
          <div className="chat-messages flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-br-md shadow-md'
                      : 'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-md border border-gray-200 dark:border-gray-600 shadow-sm'
                  }`}
                >
                  <div className="text-sm">{message.text}</div>
                  <div className={`text-xs mt-1 ${message.sender === 'user' ? 'text-purple-100' : 'text-gray-500 dark:text-gray-400'}`}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-2xl rounded-bl-md px-4 py-3 border border-gray-200 dark:border-gray-600 shadow-sm">
                  <div className="flex items-center">
                    <div className="typing-dot w-2 h-2 bg-gray-500 rounded-full mx-1 animate-bounce"></div>
                    <div className="typing-dot w-2 h-2 bg-gray-500 rounded-full mx-1 animate-bounce delay-100"></div>
                    <div className="typing-dot w-2 h-2 bg-gray-500 rounded-full mx-1 animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            {messages.length === 1 && suggestedQuestions.length > 0 && !isLoading && (
              <div className="suggested-questions flex flex-wrap gap-2 mt-2">
                {suggestedQuestions.map((question, index) => (
                  <DynamicButton
                    key={index}
                    variant="secondary"
                    size="small"
                    onClick={() => handleSuggestedQuestion(question)}
                    className="text-xs py-2 px-3 rounded-full"
                  >
                    {question}
                  </DynamicButton>
                ))}
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="chat-input-area p-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 rounded-b-3xl">
            <div className="flex gap-2">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask about robotics, AI, ROS, etc..."
                disabled={isLoading}
                rows={1}
                className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-pink-500 shadow-sm"
              />
              <DynamicButton 
                onClick={handleSend} 
                disabled={isLoading || !inputValue.trim()}
                variant="primary"
                className="self-end rounded-xl shadow-sm"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  </div>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </DynamicButton>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 text-center">
              <span className="hidden sm:inline">🤖 Built with RAG • Always learning</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;