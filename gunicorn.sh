#!/bin/bash

# Navigate to the project directory
cd /root/InstantDigitsApi2

# Activate the virtual environment
source venv/bin/activate

# Start Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 30 --access-logfile gunicorn.log --error-logfile gunicornError.log app:app
