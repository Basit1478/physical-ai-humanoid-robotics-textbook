import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import styles from './CustomFeatures.module.css';
import { personalizeApi } from '@site/src/api';

const PersonalizationButton = () => {
  const [showModal, setShowModal] = useState(false);
  const [profile, setProfile] = useState({
    education_level: 'intermediate',
    field_of_study: 'robotics',
    background: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [profileExists, setProfileExists] = useState(false);

  // Load user profile on component mount
  useEffect(() => {
    const loadProfile = async () => {
      try {
        // In a real app, we would get the actual user ID from auth context
        // For now, we'll use a placeholder user ID
        const userId = localStorage.getItem('userId') || `user_${Date.now()}`;
        if (userId) {
          // For now, just check if we can get user preferences from localStorage
          // since the backend doesn't have a specific endpoint for getting user profile
          const savedProfile = localStorage.getItem('userProfile');
          if (savedProfile) {
            const profileData = JSON.parse(savedProfile);
            setProfileExists(true);
            setProfile(profileData);
          }
        }
      } catch (error) {
        // Profile doesn't exist yet, which is fine
        console.log('No existing profile found, user needs to create one');
      }
    };

    loadProfile();
  }, []);

  const handleSaveProfile = async () => {
    setIsLoading(true);

    try {
      // Store user profile in localStorage for now
      // In a real app, we would send this to the backend for auth signup
      localStorage.setItem('userProfile', JSON.stringify(profile));

      // Also store this information when user signs up
      localStorage.setItem('userBackground', JSON.stringify({
        software_background: profile.education_level,
        hardware_background: profile.field_of_study
      }));

      setProfileExists(true);
      setShowModal(false);
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Failed to save profile. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickSetup = async () => {
    setIsLoading(true);

    try {
      // Prepare quick setup profile data
      const quickSetupProfile = {
        education_level: 'beginner',
        field_of_study: 'robotics',
        background: 'Quick setup user'
      };

      // Store user profile in localStorage for now
      localStorage.setItem('userProfile', JSON.stringify(quickSetupProfile));

      // Also store this information when user signs up
      localStorage.setItem('userBackground', JSON.stringify({
        software_background: 'beginner',
        hardware_background: 'robotics'
      }));

      setProfileExists(true);
      setProfile(quickSetupProfile);
      setShowModal(false);
      alert('Quick setup completed successfully!');
    } catch (error) {
      console.error('Error in quick setup:', error);
      alert('Failed to complete quick setup. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.customFeature}>
      <h3>Personalization</h3>
      <p>Customize your learning experience based on your background and interests:</p>

      <button
        onClick={() => setShowModal(true)}
        className={clsx('button button--secondary', styles.customButton)}
      >
        {profileExists ? 'Update Profile' : 'Create Profile'}
      </button>

      {showModal && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <h3>Personalization Profile</h3>

            <div className={styles.formGroup}>
              <label>Education Level:</label>
              <select
                value={profile.education_level}
                onChange={(e) => setProfile({...profile, education_level: e.target.value})}
                className={styles.formControl}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label>Field of Study:</label>
              <select
                value={profile.field_of_study}
                onChange={(e) => setProfile({...profile, field_of_study: e.target.value})}
                className={styles.formControl}
              >
                <option value="robotics">Robotics</option>
                <option value="computer science">Computer Science</option>
                <option value="electrical engineering">Electrical Engineering</option>
                <option value="mechanical engineering">Mechanical Engineering</option>
                <option value="general">General Interest</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label>Background (Optional):</label>
              <textarea
                value={profile.background}
                onChange={(e) => setProfile({...profile, background: e.target.value})}
                placeholder="Tell us about your background in AI/Robotics..."
                className={styles.formControl}
                rows={3}
              />
            </div>

            <div className={styles.modalActions}>
              <button
                onClick={() => setShowModal(false)}
                className="button button--outline"
              >
                Cancel
              </button>

              <button
                onClick={handleQuickSetup}
                disabled={isLoading}
                className="button button--warning"
              >
                Quick Setup
              </button>

              <button
                onClick={handleSaveProfile}
                disabled={isLoading}
                className="button button--success"
              >
                {isLoading ? 'Saving...' : 'Save Profile'}
              </button>
            </div>
          </div>
        </div>
      )}

      {profileExists && (
        <div className={styles.profileDisplay}>
          <h4>Your Current Profile:</h4>
          <ul>
            <li><strong>Education Level:</strong> {profile.education_level}</li>
            <li><strong>Field of Study:</strong> {profile.field_of_study}</li>
            <li><strong>Background:</strong> {profile.background || 'Not specified'}</li>
          </ul>
        </div>
      )}

      <p><small>Powered by AI to customize your learning experience based on your background and preferences.</small></p>
    </div>
  );
};

export default PersonalizationButton;