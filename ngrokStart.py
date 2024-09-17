import subprocess

def run_command(command):
    """Run a shell command and print its output."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print(stdout.decode())
    else:
        print(stderr.decode())

def setup_ngrok():
    # Add ngrok authtoken to the configuration
    authtoken = "2mCqd3hyYiECU0cWWW1KJdwZ0Bw_4QVsPn4mdQfkR4SxPBaci"
    print("Adding ngrok authtoken...")
    run_command(f"ngrok config add-authtoken {authtoken}")

    # Start ngrok with a static domain
    domain = "uniformly-capable-blowfish.ngrok-free.app"
    port = 5000
    print(f"Starting ngrok tunnel on port {port} with domain {domain}...")
    run_command(f"ngrok http --domain={domain} {port}")

if __name__ == "__main__":
    setup_ngrok()
