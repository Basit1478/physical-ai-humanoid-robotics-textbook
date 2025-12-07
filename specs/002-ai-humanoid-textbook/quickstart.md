# Quickstart Guide: AI Humanoid Robotics Textbook

## Overview
This guide provides a quick introduction to setting up and using the AI Humanoid Robotics Textbook project. It covers the essential steps to get started with the platform and begin learning about physical AI and humanoid robotics.

## Prerequisites
- Node.js (v18 or higher)
- Python (v3.11 or higher)
- Git
- Basic knowledge of robotics concepts (helpful but not required)

## Setting Up the Textbook Platform

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-humanoid-textbook
```

### 2. Set Up the Textbook Frontend (Docusaurus)
```bash
cd book
npm install
```

### 3. Set Up the Backend Services
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the backend directory with the following:
```env
DATABASE_URL=sqlite:///./textbook.db
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### 5. Start the Development Servers

**For the textbook frontend:**
```bash
cd book
npm start
```
This will start the Docusaurus server on http://localhost:3000

**For the backend services:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
This will start the FastAPI server on http://localhost:8000

## Navigating the Textbook Content

### Module Structure
The textbook is organized into 4 main modules:

1. **The Robotic Nervous System (ROS 2)** - Introduction to ROS 2 architecture and concepts
2. **The Digital Twin (Gazebo & Unity)** - Simulation environments for robotics
3. **The AI-Robot Brain (NVIDIA Isaac)** - AI integration in robotics
4. **Vision-Language-Action (VLA)** - Advanced perception and action systems

### Chapter Format
Each chapter includes:
- Learning outcomes at the beginning
- Detailed explanations with text-described diagrams
- Practical examples and implementation workflows
- Chapter summary at the end

## Using the API

### Base URL
The API is available at `http://localhost:8000` in development mode.

### Example API Calls

**Get all modules:**
```bash
curl http://localhost:8000/modules
```

**Get a specific chapter:**
```bash
curl http://localhost:8000/chapters/module1-chapter1
```

**Update user progress:**
```bash
curl -X POST http://localhost:8000/users/user123/progress \
  -H "Content-Type: application/json" \
  -d '{
    "chapterId": "module1-chapter1",
    "completed": true,
    "notes": "Great chapter on ROS 2 architecture",
    "rating": 5
  }'
```

## Personalization Features

### User Profiles
The platform supports personalized learning experiences:
- Track your progress through modules and chapters
- Save notes and bookmarks
- Set learning preferences

### Content Adaptation
- Adjust content difficulty based on your background
- Access supplementary materials tailored to your learning style
- Get recommendations for next chapters based on your progress

## Translation Support

The platform supports multiple languages:
- Switch languages using the language selector in the UI
- Currently supports Urdu translation (with more coming)
- Contribute translations through the translation API

## Development Workflow

### Adding New Content
1. Create a new markdown file in the appropriate module directory in `book/`
2. Follow the chapter template structure
3. Update `sidebars.ts` to include the new chapter in navigation
4. Update the API contracts if adding new functionality

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd book
npm test
```

### Building for Production
```bash
# Build the Docusaurus site
cd book
npm run build

# The built site will be in the build/ directory and can be served statically
```

## Troubleshooting

### Common Issues

**Frontend not loading properly:**
- Clear your browser cache
- Run `npm install` again to ensure all dependencies are present

**Backend API errors:**
- Check that the backend server is running on port 8000
- Verify your environment variables are set correctly
- Check the backend logs for specific error messages

**Content not appearing:**
- Ensure the content file is in the correct directory
- Verify the sidebar configuration includes your content
- Restart the development server after adding new files

## Next Steps

1. Begin with Module 1: The Robotic Nervous System to establish foundational concepts
2. Use the progress tracking features to monitor your learning journey
3. Explore the interactive examples and code snippets
4. Engage with the community through the discussion forums
5. Contribute to the project by suggesting improvements or adding content