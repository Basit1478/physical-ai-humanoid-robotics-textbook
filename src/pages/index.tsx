import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Read Textbook
          </Link>
        </div>
      </div>
    </header>
  );
}

function ModuleCard({ title, description, url }) {
  return (
    <div className={styles.moduleCard}>
      <h3>{title}</h3>
      <ul>
        {description.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
      <div className={styles.buttonContainer}>
        <Link
          className={styles.cardButton}
          to={url}>
          Learn More
        </Link>
      </div>
    </div>
  );
}

function ModuleCardsSection() {
  const modules = [
    {
      title: "Module 1: The Robotic Nervous System (ROS 2)",
      description: [
        "Introduction to ROS 2 architecture and concepts",
        "Communication patterns and implementation best practices",
        "Advanced ROS 2 development techniques"
      ],
      url: "/docs/module1/chapter1"
    },
    {
      title: "Module 2: The Digital Twin (Gazebo & Unity)",
      description: [
        "Gazebo simulation environment for robotics",
        "Unity integration for advanced robotics applications",
        "Digital twin concepts and practical applications"
      ],
      url: "/docs/module2/chapter1"
    },
    {
      title: "Module 3: The AI-Robot Brain (NVIDIA Isaac)",
      description: [
        "NVIDIA Isaac platform overview and capabilities",
        "AI-robot integration patterns and implementation workflows",
        "Advanced robotics AI systems and deployment strategies"
      ],
      url: "/docs/module3/chapter1"
    },
    {
      title: "Module 4: Vision-Language-Action (VLA)",
      description: [
        "Vision-language-action systems overview",
        "Vision processing and perception in VLA systems",
        "Action planning and execution in integrated systems"
      ],
      url: "/docs/module4/chapter1"
    },
    {
      title: "Module 5: Capstone Project - Building an Autonomous Humanoid Robot System",
      description: [
        "Integration of all previous modules into a complete system",
        "Real-world deployment and validation",
        "Advanced robotics project management and execution"
      ],
      url: "/docs/module5/chapter1"
    }
  ];

  return (
    <section className={styles.modulesSection}>
      <div className="container">
        <Heading as="h2" className={styles.sectionTitle}>
          Course Structure
        </Heading>
        <p className={styles.sectionDescription}>
          The textbook is organized into five comprehensive modules with increasing complexity:
        </p>
        <div className={styles.modulesGrid}>
          {modules.map((module, index) => (
            <ModuleCard
              key={index}
              title={module.title}
              description={module.description}
              url={module.url}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="Physical AI & Humanoid Robotics Textbook - Advanced STEM Learning for Embodied Intelligence">
      <HomepageHeader />
      <main>
        <ModuleCardsSection />
      </main>
    </Layout>
  );
}
