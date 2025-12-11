#!/usr/bin/env bash
# Render deployment start script
python -m uvicorn main:app --host 0.0.0.0 --port $PORT