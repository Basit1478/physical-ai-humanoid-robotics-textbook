import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

// Root component wrapper to add ChatWidget to all pages
export default function Root({children}) {
  return (
    <>
      {children}
      <BrowserOnly fallback={<div />}>
        {() => {
          const ChatWidget = require('@site/src/components/ChatWidget').default;
          return <ChatWidget />;
        }}
      </BrowserOnly>
    </>
  );
}
