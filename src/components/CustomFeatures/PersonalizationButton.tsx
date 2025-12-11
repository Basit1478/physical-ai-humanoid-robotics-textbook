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
          const userProfile = await personalizeApi.getUserProfile(userId);
          if (userProfile) {
            setProfileExists(true);
            // Update profile state based on the retrieved profile
            setProfile({
              education_level: userProfile.level || 'intermediate',
              field_of_study: userProfile.interests?.[0] || 'robotics',
              background: userProfile.additional_preferences?.background || ''
            });
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
      // Prepare user preferences data for the API
      const userPreferences = {
        user_id: `user_${Date.now()}`, // In a real app, this would come from auth
        interests: [profile.field_of_study],
        level: profile.education_level,
        learning_style: 'visual', // Default value
        preferred_language: 'en',
        additional_preferences: {
          background: profile.background,
          field_of_study: profile.field_of_study
        }
      };

      // Call the backend personalization API
      await personalizeApi.setPreferences(userPreferences);
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
      // Prepare quick setup preferences data for the API
      const quickSetupPreferences = {
        user_id: `user_${Date.now()}`, // In a real app, this would come from auth
        interests: ['robotics', 'ai'],
        level: 'beginner',
        learning_style: 'visual',
        preferred_language: 'en',
        additional_preferences: {
          background: 'Quick setup user',
          field_of_study: 'robotics'
        }
      };

      // Call the backend personalization API
      await personalizeApi.setPreferences(quickSetupPreferences);
      setProfileExists(true);
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