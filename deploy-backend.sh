#!/bin/bash

# Production deployment script for backend API

echo "Starting backend API production deployment..."

# Check if docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start services
echo "Building and starting services..."
docker-compose up -d --build

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check if services are running
echo "Checking service status..."
docker-compose ps

echo "Deployment completed!"
echo "Backend API is now running at http://localhost:8000"
echo "API documentation is available at http://localhost:8000/api/docs"