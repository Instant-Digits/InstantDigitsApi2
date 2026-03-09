#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/InstantDigitsApi3

# Activate the virtual environment
source venv/bin/activate

# Kill any existing ngrok processes
pkill ngrok 

# Kill any existing uvicorn processes
pkill -f "uvicorn main:app"

# Run the ngrok setup script in the background ngrok not using now
#python ngrokStart.py &

# Start Gunicorn with nohup to keep running after logout
nohup uvicorn main:app --host 0.0.0.0 --port 5000 --log-level info > uvicorn.log 2>&1 &


# Print the process IDs for debugging
echo "ngrok PID: $!"
echo "Gunicorn PID: $!"
