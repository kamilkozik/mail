import pathlib
from concurrent.futures import ThreadPoolExecutor
from typing import List

from classifiers import MagicClassifier
from files import GoogleFileMeta, FileMeta
from gdrive import GoogleDrive
from invoices import InvoiceDetector
from logger import get_logger


class InvoicesPipeline:

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self._detectors = [InvoiceDetector()]

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
#        with ThreadPoolExecutor(max_workers=2) as pool:
#            threads = [
#                pool.submit(google_drive.upload_file, file, target_folder)
#                for file in files
#            ]
#            for t in threads:
#                t.result()

    @staticmethod
    def _get_folder_content(folder: GoogleFileMeta, google_drive: GoogleDrive) -> List[GoogleFileMeta]:
        return [f for f in google_drive.iterate_folder_content(folder)]

    def _filter_invoices_files(self, files: List[FileMeta]) -> List[FileMeta]:
        if not files:
            return []

        for detector in self._detectors:
            files = [f for f in files if detector.is_invoice(f.path, MagicClassifier())]

        return files

    def run(self, files: List[FileMeta], target: pathlib.Path, google_drive: GoogleDrive):
        target_folder = self._get_folder_by_path(target, google_drive)
        folder_files = self._get_folder_content(target_folder, google_drive)
        existing_files = [f.name for f in folder_files]
        files = list(filter(lambda file: file.name not in existing_files, files))

        if not files:
            self.logger.info(f'No new files to upload')
            return

        files = self._filter_invoices_files(files)
        self._upload_files(files, target_folder, google_drive)
