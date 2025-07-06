import requests

url = "http://localhost:8000/files/uploadAFile"
file_path = "req.txt"  # Path to your file
folder = "testfolder"  # Specify your subfolder here

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "text/x-python")}
    data = {"folder": folder}
    response = requests.post(url, files=files, data=data)

print("Upload response:", response.json())

# Get the uploaded file's relative path for deletion
def delete_uploaded_file(relative_path):
    url = "http://localhost:8000/files/deleteAFile/"
    payload = {"url": relative_path}
    response = requests.post(url, json=payload)
    return response.json()

# Example usage:
relative_path = f"{folder}/{file_path}"
result = delete_uploaded_file(relative_path)
print("Delete response:", result)
