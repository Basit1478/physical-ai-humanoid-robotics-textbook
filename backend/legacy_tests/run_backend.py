import subprocess
import sys
import os

# Change to the backend directory and run the server
backend_dir = "C:\\Users\\Windows 10 Pro\\Desktop\\hackathon book 1\\backend"
os.chdir(backend_dir)
subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])