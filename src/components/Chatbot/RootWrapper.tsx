import React, { useEffect } from 'react';
import { useLocation } from '@docusaurus/router';
import Chatbot from './Chatbot';

// Root component that will be used globally
const Root = ({ children }) => {
  const location = useLocation();

  useEffect(() => {
    // Any global initialization can go here
    // This runs on every route change
  }, [location]);

  return (
    <>
      {children}
      <Chatbot />
    </>
  );
};

export default Root;