from __future__ import print_function

import io
import pathlib
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from files import FileMeta, GoogleFileMeta, GoogleMimeTypes
from logger import get_logger

SCOPES = ['https://www.googleapis.com/auth/drive']


class MultipleFilesError(Exception):
    pass


class GoogleOAuth:
    credentials: Credentials = None

    def _set_credentials(self, token_path: pathlib.Path) -> None:
        if token_path.exists() and token_path.is_file():
            self.credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    @property
    def _has_credentials(self) -> bool:
        return self.credentials is not None

    def _refresh_credentials(self):
        self.credentials.refresh(Request())

    def _login(self, token_path: pathlib.Path, credentials_path: pathlib.Path):
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        self.credentials = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(self.credentials.to_json())

    def authorize(self, token_path: pathlib.Path, credentials_path: pathlib.Path):
        self._set_credentials(token_path)

        if self.credentials.expired:
            self._login(token_path, credentials_path)


class GoogleDrive:
    def __init__(self, drive_service):
        self.service = drive_service
        self.logger = get_logger(self.__class__.__name__)

    @staticmethod
    def _get_media(file: FileMeta):
        return MediaFileUpload(file.path, mimetype=file.mime_type)

    @staticmethod
    def _get_body(file: FileMeta) -> dict:
        return {'name': file.name}

    @staticmethod
    def _build_query(params: dict) -> str:
        return ' and '.join(
            f'{name}{operation["operator"]}{operation["value"]}'
            for name, operation in params.items()
        )

    def get_folder(self, folder_name: str, parent_folder: GoogleFileMeta = None) -> GoogleFileMeta:
        """
        Returns folder id. Raises MultipleFilesError if multiple folders returned and NoFilesFoundError if no match.
        :param parent_folder:
        :param folder_name:
        :return: GoogleFileMeta
        """
        params = {
            'name': {'operator': '=', 'value': f'\'{folder_name}\''},
            'mimeType': {'operator': '=', 'value': f'\'{GoogleMimeTypes.FOLDER.value}\''}
        }
        if parent_folder:
            params.update({
                f'\'{parent_folder.object_id}\'': {
                    'operator': ' in ',
                    'value': 'parents'
                }
            })
        query = self._build_query(params)
        files = self.service.files().list(q=query, fields='files(name, id, mimeType)').execute()
        files = files.get('files')

        if len(files) > 1:
            raise MultipleFilesError(f'Multiple folders returned for name {folder_name}')
        elif len(files) < 1:
            raise FileNotFoundError(f'Could not find {folder_name} folder name')

        return GoogleFileMeta(files[0])

    def create_folder(self, folder_name: str, target_folder: GoogleFileMeta = None) -> GoogleFileMeta:
        """
        Creates folder in the Google drive target_folder if provided, otherwise creates in root directory.
        :param target_folder: Google drive folder where the folder_name will be created.
        :param folder_name: Name of the folder
        :return: Id of the folder
        """
        body = {
            'name': folder_name,
            'mimeType': GoogleMimeTypes.FOLDER.value
        }
        if target_folder:
            body.update({'parents': [target_folder.object_id]})

        folder = self.service.files().create(body=body, fields='id, name, mimeType').execute()
        return GoogleFileMeta(folder)

    def get_file_meta(self, file_id: str) -> GoogleFileMeta:
        file = self.service.files().get(fileId=file_id).execute()
        return GoogleFileMeta(file)

    def upload_file(self, file: FileMeta, parent_folder: GoogleFileMeta = None) -> GoogleFileMeta:
        """
        Upload file to the Google drive
        :param parent_folder: Upload file into provided folder id, if none upload to root of Google drive
        :param file: Path to the file to be uploaded
        :return: None
        """
        self.logger.info(f'Uploading {file.name} to {parent_folder.name if parent_folder else "root"}')
        media = self._get_media(file)
        body = self._get_body(file)

        if parent_folder:
            body.update({'parents': [parent_folder.object_id]})

        file = self.service.files().create(body=body, media_body=media, fields='id, name, mimeType').execute()
        return GoogleFileMeta(file)

    def remove_file(self, file_id: str) -> None:
        """
        Remove file from Google drive
        :param file_id: Google file id
        :return: None
        """
        raise NotImplemented()

    def download_file(self, file_object: GoogleFileMeta, target: pathlib.Path) -> None:
        request = self.service.files().get_media(fileId=file_object.object_id)
        target_file_path = target / file_object.name
        fh = io.FileIO(str(target_file_path), 'wb')
        downloader = MediaIoBaseDownload(fh, request, chunksize=5 * 1024 * 1024)
        done = False
        while done is False:
            _, done = downloader.next_chunk()
            self.logger.info(f"Downloading {file_object.name}")

    def iterate_folder_content(self, folder_meta: GoogleFileMeta) -> List[GoogleFileMeta]:
        """
        Iterate Google folder content
        :param folder_meta: Google folder to iterate contents
        :return: List of files metadata in the given Google folder
        """
        params = {
            f'\'{folder_meta.object_id}\'': {
                'operator': ' in ',
                'value': 'parents'
            }
        }
        query = self._build_query(params)

        next_page_token = None
        while True:
            response = self.service.files().list(
                q=query,
                pageSize=10,
                fields='files(name, id, mimeType), nextPageToken',
                pageToken=next_page_token
            ).execute()

            for file in response.get('files'):
                yield GoogleFileMeta(file)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
