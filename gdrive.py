from __future__ import print_function

import io
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# If modifying these scopes, delete the file token.pickle.
from googleapiclient.http import MediaIoBaseDownload

from consts import ATTACHMENTS_PATH, GOOGLE_DRIVE_SCOPES
from utils import get_month_year


def get_credentials():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', GOOGLE_DRIVE_SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return credentials


def get_files_id_by_name(service, name, mime, exact=False):
    query = f"name='{name}'" if exact else f"name contains '{name}'"
    result = service.files().list(q=f"mimeType='{mime}' and {query}", fields="files(id, name, mimeType)").execute()
    return [f['id'] for f in result.get('files', [])]


def get_files_by_parents_id(service, fid):
    result = service.files().list(q=f"'{fid}' in parents", fields="files(id, name, mimeType)").execute()
    return result.get('files', [])


def fetch_files():
    folder_mime = 'application/vnd.google-apps.folder'
    business_folder_name = 'faktury'
    month, year = get_month_year()
    service = build('drive', 'v3', credentials=get_credentials())
    ids = get_files_id_by_name(service, business_folder_name, folder_mime)

    files = []
    for fid in ids:
        for year_elem in filter(lambda o: o['name'] == year, get_files_by_parents_id(service, fid)):
            response = service.files().list(
                q=f"'{year_elem['id']}' in parents and name='{month}'", fields="files(id, name, mimeType)"
            ).execute()

            for end_file in response.get('files', []):
                files.extend(get_files_by_parents_id(service, end_file['id']))

    for item in files:
        if 'folder' in item['mimeType']:
            continue

        print(u'{0} ({1})'.format(item['name'], item['id']))
        request = service.files().get_media(fileId=item['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done:
            status, done = downloader.next_chunk()
            print(f"Download: {int(status.progress() * 100)}%")
        fh.seek(0)

        if not os.path.exists(ATTACHMENTS_PATH):
            os.mkdir(ATTACHMENTS_PATH)
        with open(os.path.join(ATTACHMENTS_PATH, item['name']), 'wb') as f:
            f.write(fh.read())


def flush():
    for file in [os.path.join(ATTACHMENTS_PATH, f) for f in os.listdir(ATTACHMENTS_PATH)]:
        os.remove(file)
        print(f"Removed: {file.split('/')[-1]}")
