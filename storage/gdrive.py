from __future__ import print_function

import io
import os.path

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from misc.utils import get_month_year
from settings.base import ATTACHMENTS_PATH
from storage.auth import get_credentials


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
        for year_elem in filter(lambda o: o['name'] == str(year), get_files_by_parents_id(service, fid)):
            response = service.files().list(
                q=f"'{year_elem['id']}' in parents and name='{month if month > 9 else f'0{month}'}'",
                fields="files(id, name, mimeType)"
            ).execute()

            for end_file in response.get('files', []):
                files.extend(get_files_by_parents_id(service, end_file['id']))

    for item in files:
        if 'folder' in item['mimeType']:
            continue

        print(u'{0} ({1})'.format(item['name'], item['id']), end=" - ")
        request = service.files().get_media(fileId=item['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done == False:
            status, done = downloader.next_chunk()
            print(f"Download: {int(status.progress() * 100)}%")
        fh.seek(0)

        if not os.path.exists(ATTACHMENTS_PATH):
            os.mkdir(ATTACHMENTS_PATH)
        count = 1
        while True:
            if os.path.exists(os.path.join(ATTACHMENTS_PATH, item['name'])):
                item['name'] = f'{count}' + item['name']
            else:
                break

        with open(os.path.join(ATTACHMENTS_PATH, item['name']), 'wb') as f:
            f.write(fh.read())


def flush():
    if os.path.exists(ATTACHMENTS_PATH):
        for file in [os.path.join(ATTACHMENTS_PATH, f) for f in os.listdir(ATTACHMENTS_PATH)]:
            os.remove(file)
            print(f"Removed: {file.split('/')[-1]}")
