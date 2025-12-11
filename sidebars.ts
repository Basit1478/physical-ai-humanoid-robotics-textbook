import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Main textbook sidebar organized by modules
  textbookSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro'],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module1/chapter1',
        'module1/chapter2',
        'module1/chapter3'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      items: [
        'module2/chapter1',
        'module2/chapter2',
        'module2/chapter3'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac)',
      items: [
        'module3/chapter1',
        'module3/chapter2',
        'module3/chapter3'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'module4/chapter1',
        'module4/chapter2',
        'module4/chapter3'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'References',
      items: [
        'references/bibliography',
        'references/citations'
      ],
      collapsed: true,
    },
    {
      type: 'category',
      label: 'Interactive Features',
      items: [
        'demo'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Developer Resources',
      items: [
        'integration-guide'
      ],
      collapsed: true,
    },
  ],
};

export default sidebars;