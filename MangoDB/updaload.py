from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os.path

#pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# If modifying these SCOPES, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_google_drive():
    """Shows basic usage of the Drive v3 API."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creditial.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def upload_file_to_google_drive(file_path):
    """Uploads a file to Google Drive"""
    creds = authenticate_google_drive()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')

    # Upload the file
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"File ID: {file.get('id')} uploaded successfully.")

# Replace with the path to the file you want to upload
file_path = 'app.py'
upload_file_to_google_drive(file_path)
