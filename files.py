import abc
import enum
import mimetypes
import pathlib


def guess_file_mime_type(file_path: pathlib.Path) -> str:
    f_type, _ = mimetypes.guess_type(file_path)
    return f_type


class GoogleMimeTypes(enum.Enum):
    FOLDER = 'application/vnd.google-apps.folder'


class AbstractFileMeta(abc.ABC):
    def __str__(self):
        return f'<{self.__class__.__name__} name=\'{self.name}\' mime_type=\'{self.mime_type}\'>'

    def __repr__(self):
        return self.__str__()

    @property
    @abc.abstractmethod
    def mime_type(self) -> str:
        raise NotImplemented()

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplemented()


class FileMeta(AbstractFileMeta):
    def __init__(self, file_path: pathlib.Path):
        self.path = file_path


    @property
    def mime_type(self) -> str:
        return guess_file_mime_type(self.path)

    @property
    def name(self) -> str:
        return self.path.name


class GoogleFileMeta(AbstractFileMeta):
    def __init__(self, response: dict):
        self.response = response

    @property
    def mime_type(self) -> str:
        return self.response.get('mimeType')

    @property
    def name(self) -> str:
        return self.response.get('name')

    @property
    def object_id(self) -> str:
        return self.response.get('id')
