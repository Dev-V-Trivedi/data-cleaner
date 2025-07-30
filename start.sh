#!/bin/bash

# Install dependencies with fallback
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt || echo "Some packages failed to install, continuing..."

# Alternative: Install core packages individually
pip install fastapi uvicorn python-multipart || echo "Core packages installation failed"

# Try to install pandas and numpy
pip install pandas numpy || echo "Pandas/NumPy installation failed, will use simple classifier"

# Start the application - FIXED COMMAND
echo "Starting application..."
uvicorn main_robust:app --host 0.0.0.0 --port $PORT
