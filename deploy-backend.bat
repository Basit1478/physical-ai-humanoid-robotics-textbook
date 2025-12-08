@echo off
REM Production deployment script for backend API on Windows

echo Starting backend API production deployment...

REM Check if docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Compose is not installed. Please install Docker Desktop which includes Docker Compose.
    exit /b 1
)

REM Build and start services
echo Building and starting services...
docker-compose up -d --build

REM Wait for services to start
echo Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check if services are running
echo Checking service status...
docker-compose ps

echo Deployment completed!
echo Backend API is now running at http://localhost:8000
echo API documentation is available at http://localhost:8000/api/docs