import pathlib
from typing import List

from files import GoogleFileMeta, FileMeta
from gdrive import GoogleDrive
from logger import get_logger


class InvoicesPipeline:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @staticmethod
    def _get_folder(google_drive: GoogleDrive, create: bool = False, **params) -> GoogleFileMeta:
        try:
            folder = google_drive.get_folder(**params)
        except FileNotFoundError:
            if not create:
                raise
            folder = google_drive.create_folder(
                folder_name=params['folder_name'],
                target_folder=params['parent_folder']
            )

        return folder

    def _get_folder_by_path(self, folder_path: pathlib.Path, google_drive: GoogleDrive) -> GoogleFileMeta:
        parts = folder_path.parts
        if not len(parts):
            raise ValueError(f'Wrong value in folder_path: {folder_path}')

        parent_folder = None
        for folder_name in parts:
            params = {
                'folder_name': folder_name,
                'parent_folder': parent_folder
            }
            parent_folder = self._get_folder(google_drive, create=True, **params)

        return parent_folder

    @staticmethod
    def _upload_files(files: List[FileMeta], target_folder: GoogleFileMeta, google_drive: GoogleDrive):
        for file in files:
            google_drive.upload_file(file, target_folder)

    @staticmethod
    def _get_folder_content(folder: GoogleFileMeta, google_drive: GoogleDrive) -> List[GoogleFileMeta]:
        return [f for f in google_drive.iterate_folder_content(folder)]

    def run(self, files: List[FileMeta], target: pathlib.Path, google_drive: GoogleDrive):
        target_folder = self._get_folder_by_path(target, google_drive)
        folder_files = self._get_folder_content(target_folder, google_drive)
        existing_files = [f.name for f in folder_files]
        files = list(filter(lambda file: file.name not in existing_files, files))

        if not files:
            self.logger.info(f'No new files to upload')
            return

        self._upload_files(files, target_folder, google_drive)