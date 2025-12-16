import React from 'react';
import Chatbot from '../components/Chatbot/Chatbot';

// Root component that wraps the entire application
// Chatbot integrated globally via Root theme component
const Root = ({ children }) => {
  return (
    <>
      {children}
      <Chatbot />
    </>
  );
};

export default Root;