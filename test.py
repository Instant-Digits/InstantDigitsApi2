import requests
api ='https://apis.instantdigits.com'
url = f"{api}/files/uploadAFile"
file_path = "test.mp4"  # Path to your file
folder = "testfolder"  # Specify your subfolder here

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "video/mp4")}
    data = {"folder": folder}
    response = requests.post(url, files=files, data=data)

print("Upload response:", response.json())

# Get the uploaded file's relative path for deletion
def delete_uploaded_file(relative_path):
    url = f"{api}/files/deleteAFile/"
    payload = {"url": relative_path}
    response = requests.post(url, json=payload)
    return response.json()

# Example usage:
# relative_path = f"{folder}/{file_path}"
# result = delete_uploaded_file(relative_path)
# print("Delete response:", result)
