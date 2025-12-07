#!/bin/bash

# Setup script for Physical AI & Humanoid Robotics Textbook repository

echo "Setting up the Physical AI & Humanoid Robotics Textbook repository..."

# Initialize git if not already done
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
fi

# Set up the remote origin
git remote set-url origin https://github.com/basit1478/physical-ai-humanoid-robotics-textbook.git

# Set main branch
git branch -M main

echo "Git repository configured!"
echo ""
echo "To complete the setup:"
echo "1. Create the repository on GitHub at https://github.com/basit1478/physical-ai-humanoid-robotics-textbook"
echo "2. Run: git push -u origin main"
echo ""
echo "After pushing, GitHub Actions will automatically build and deploy your site to GitHub Pages."
echo "Your site will be available at: https://basit1478.github.io/physical-ai-humanoid-robotics-textbook/"