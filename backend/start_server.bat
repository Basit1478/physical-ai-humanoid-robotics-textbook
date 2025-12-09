@echo off
REM Script to start the backend server
echo Starting Textbook Project Backend...

REM Install dependencies
pip install -r requirements.txt

REM Run the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload