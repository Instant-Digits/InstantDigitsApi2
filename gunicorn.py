import subprocess
import sys
import os

def start_gunicorn():
    try:
        # Define the path to the project directory and Gunicorn executable
        project_dir = '/root/InstantDigitsApi2'
        venv_bin = os.path.join(project_dir, 'venv', 'bin', 'gunicorn')

        # Define the Gunicorn command
        gunicorn_command = [
            venv_bin,                           # Path to Gunicorn in the venv
            '-w', '4',                         # Number of worker processes
            '-b', '0.0.0.0:5000',              # Bind address and port
            '--timeout', '30',                 # Timeout for requests
            '--access-logfile', 'gunicorn.log', # Access log file
            '--error-logfile', 'gunicornError.log', # Error log file
            'app:app'                           # Replace with your Flask app's module name and application variable
        ]
        
        # Change to the project directory
        os.chdir(project_dir)
        
        # Open log files for Gunicorn
        with open('gunicorn_stdout.log', 'w') as stdout_file, open('gunicorn_stderr.log', 'w') as stderr_file:
            # Start Gunicorn and redirect output
            subprocess.run(gunicorn_command, stdout=stdout_file, stderr=stderr_file, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while starting Gunicorn: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    start_gunicorn()
