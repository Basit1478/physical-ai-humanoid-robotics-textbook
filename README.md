# Physical AI & Humanoid Robotics Textbook

This repository contains the complete source code for the Physical AI & Humanoid Robotics textbook, including both the frontend (Docusaurus website) and backend (FastAPI API) with RAG chatbot, personalization, and translation features.

**Live Site**: [https://basit1478.github.io/physical-ai-humanoid-robotics-textbook/](https://basit1478.github.io/physical-ai-humanoid-robotics-textbook/)

## About

This textbook provides comprehensive coverage of Physical AI and Humanoid Robotics, designed for advanced STEM learners in capstone AI/robotics programs focusing on embodied intelligence. The content covers the full pipeline from sensing to simulation to action to learning, with a focus on connecting digital intelligence with physical humanoid robots.

## Structure

The textbook is organized into four comprehensive modules:

1. **Module 1: The Robotic Nervous System (ROS 2)**
2. **Module 2: The Digital Twin (Gazebo & Unity)**
3. **Module 3: The AI-Robot Brain (NVIDIA Isaac)**
4. **Module 4: Vision-Language-Action (VLA)**

## Features

- **Interactive Textbook**: Built with Docusaurus for a responsive, mobile-friendly experience
- **RAG Chatbot**: Retrieval-Augmented Generation chatbot for answering questions about the content
- **Personalization**: Adaptive learning paths based on user profiles and preferences
- **Multilingual Support**: Real-time translation to Urdu and other languages
- **Authentication**: Secure user registration and login system

## Local Development

### Frontend (Docusaurus)

```bash
# Navigate to the website directory
cd my-website

# Install dependencies
npm install

# Start development server
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

### Backend (FastAPI)

```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start development server
python -m app.main
```

The backend API will be available at http://localhost:8000 with documentation at http://localhost:8000/api/docs

## Build

### Frontend

```bash
# Build the static website
npm run build
```

### Backend

The backend is containerized with Docker for production deployment:

```bash
# Build and start all services
docker-compose up -d --build
```

## Deployment

### Frontend
The site is automatically deployed to GitHub Pages when changes are pushed to the main branch using GitHub Actions.

### Backend
The backend can be deployed using Docker Compose with the provided configuration files.

## Project Structure

```
├── my-website/           # Frontend (Docusaurus)
├── backend/              # Backend API (FastAPI)
│   ├── app/              # Main application
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Database models
│   ├── auth/             # Authentication system
│   └── ...
├── docker-compose.yml    # Production deployment configuration
├── DEPLOYMENT.md         # Backend deployment guide
└── PROJECT_SUMMARY.md    # Complete project documentation
```

## Contributing

If you'd like to contribute to this textbook, please feel free to submit issues or pull requests.
