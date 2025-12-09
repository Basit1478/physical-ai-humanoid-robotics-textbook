import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';

// Root component wrapper to add ChatWidget to all pages
export default function Root({children}) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
