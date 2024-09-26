#!/bin/bash

# Navigate to the project directory
cd /root/InstantDigitsApi2

# Activate the virtual environment
source venv/bin/activate

# Kill any existing ngrok processes
pkill ngrok && pkill gunicorn

# Kill any existing gunicorn processes
#pkill gunicorn

# Run the ngrok setup script in the background
python ngrokStart.py &

# Start Gunicorn with nohup to keep running after logout
nohup gunicorn -w 4 -b 0.0.0.0:5000 --timeout 30 --access-logfile gunicorn.log --error-logfile gunicornError.log app:app > gunicorn.out 2>&1 &

# Print the process IDs for debugging
echo "ngrok PID: $!"
echo "Gunicorn PID: $!"
