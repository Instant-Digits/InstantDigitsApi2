#!/bin/bash

# Navigate to the project directory
cd /root/InstantDigitsApi2

# Activate the virtual environment
source venv/bin/activate

# Kill any existing ngrok processes
pkill ngrok 

# Kill any existing gunicorn processes

# Run the ngrok setup script in the background
python ngrokStart.py &

# Start Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 30 --access-logfile gunicorn.log --error-logfile gunicornError.log app:app 
