import React from 'react';
import clsx from 'clsx';
import styles from './CustomFeatures.module.css';
import UrduButton from './UrduButton';
import PersonalizationButton from './PersonalizationButton';
import RagChatbot from './RagChatbot';

const CustomFeatures = () => {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          <div className={clsx('col col--12')}>
            <h2 className="text--center">Interactive Learning Features</h2>
            <p className="text--center">
              Enhance your learning experience with our AI-powered tools
            </p>
          </div>
        </div>

        <div className="row">
          <div className={clsx('col col--4')}>
            <UrduButton />
          </div>
          <div className={clsx('col col--4')}>
            <PersonalizationButton />
          </div>
          <div className={clsx('col col--4')}>
            <RagChatbot />
          </div>
        </div>
      </div>
    </section>
  );
};

export default CustomFeatures;