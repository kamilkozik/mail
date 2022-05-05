import abc
import dataclasses
import pathlib

import magic


PDF = 'application/pdf'
PNG = 'image/png'
PLAIN_TEXT = 'text/plain'


@dataclasses.dataclass
class FileTypeModel:
    path: str
    mime: str

    def __str__(self):
        return f'<FileTypeModel mime=\'{self.mime}\' name=\'{self._name}\'>'

    def __repr__(self):
        return self.__str__()

    @property
    def _name(self):
        return self.path.split('/')[-1]


class FileClassifier(abc.ABC):
    @abc.abstractmethod
    def _get_file_type(self, file_path: pathlib.Path) -> FileTypeModel:
        ...

    def is_of_type(self, file_path: pathlib.Path, file_type: str) -> bool:
        type_of_file = self._get_file_type(file_path)
        return type_of_file.mime == file_type


class MagicClassifier(FileClassifier):
    def _get_file_type(self, file_path: pathlib.Path) -> FileTypeModel:
        mime_type = magic.from_file(file_path.as_posix(), mime=True)
        return FileTypeModel(path=file_path.as_posix(), mime=mime_type)
