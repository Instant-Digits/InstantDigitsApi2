import requests

# Define the URL of your Flask app
url = 'http://0.0.0.0:8000/ShinolQRGenerator'  # Update the port if needed

# Prepare the data to send
data = {
    'enData': 'Sample QR Code Data',
    'label': 'Sample Label',
    'address': '123 Sample Street'
}

# Send the POST request
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Save the PDF file
    with open('delete.pdf', 'wb') as f:
        f.write(response.content)
    print("PDF saved as 'delete.pdf'")
else:
    print(f"Error: {response.status_code} - {response.text}")
