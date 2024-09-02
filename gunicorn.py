# start_gunicorn.py
import subprocess
import sys
from pyngrok import ngrok

def start_gunicorn():
    try:
        # Define the Gunicorn command
        gunicorn_command = [
            'gunicorn', 
            '-w', '8',                 # Number of worker processes
            '-b', '0.0.0.0:8000',      # Bind address and port
            '--timeout', '30',         # Timeout for requests
            '--access-logfile', 'gunicorn.log',  # Access log file
            '--error-logfile', 'gunicornError.log',    # Error log file # Bind address and port
            'app:app'   # Replace with your Flask app's module name and application variable
        ]
        
        # Open log files for Gunicorn
        with open('gunicorn_stdout.log', 'w') as stdout_file, open('gunicorn_stderr.log', 'w') as stderr_file:
            # Start Gunicorn and redirect output
            subprocess.run(gunicorn_command, stdout=stdout_file, stderr=stderr_file, check=True)
        
    except subprocess.CalledProcessError as e:
        input(f"An error occurred while starting Gunicorn: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    ngrok.set_auth_token("2lAQy2D3FFFsk2Iq2nQV1WXTF0w_mHNMU9M8h8qw1LzL2JrV")
    url = ngrok.connect(8000, bind_tls=True, hostname="pleasing-javelin-absolutely.ngrok-free.app")
    print(f" * ngrok tunnel \"{url}\"")
    start_gunicorn()
