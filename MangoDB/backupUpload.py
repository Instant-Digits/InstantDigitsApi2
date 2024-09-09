import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Define the SCOPES
SCOPES = ['https://www.googleapis.com/auth/drive']

def getFilePath(filename):
    """Construct the full path to a file in the script's directory."""
    return os.path.join(getScriptDirectory(), filename)

def getScriptDirectory():
    """Get the directory of the script file."""
    return os.path.dirname(os.path.abspath(__file__))

def authenticateGoogleDrive():
    """Authenticate and get Google Drive API service."""
    creds = None
    tokenPath = getFilePath('token.json')
    credentialsPath = getFilePath('credentials.json')

    if os.path.exists(tokenPath):
        creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentialsPath, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(tokenPath, 'w') as token:
            token.write(creds.to_json())

    return creds

def uploadOrUpdateFile(filePath, fileId=None):
    """Uploads a new file or updates an existing file on Google Drive."""
    creds = authenticateGoogleDrive()
    service = build('drive', 'v3', credentials=creds)
    
    fileMetadata = {'name': os.path.basename(filePath)}
    media = MediaFileUpload(filePath, mimetype='application/octet-stream')

    if fileId:
        # Update existing file
        file = service.files().update(
            fileId=fileId,
            body=fileMetadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"File ID: {file.get('id')} updated successfully.")
    else:
        # Create a new file
        file = service.files().create(
            body=fileMetadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"File ID: {file.get('id')} uploaded successfully.")
    
    return file.get('id')

# Example usage:
if __name__ == "__main__":
    # Replace with the path to the file you want to upload
    filePath = getFilePath('token.json')
    
    # Replace 'your_existing_file_id' with the ID of the file you want to update, if any
    existingFileId = '1Zd0RrS1cRfi8flwT80zwLr6o9fAOPcUi'  # or None if uploading a new file
    
    uploadOrUpdateFile(filePath, fileId=existingFileId)
