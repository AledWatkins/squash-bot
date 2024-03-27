import abc
import pathlib

from squash_bot.settings import base as settings_base


class StorageBackend(abc.ABC):
    @abc.abstractmethod
    def store_file(self, file_path: str, file_name: str, contents: str) -> None: ...

    @abc.abstractmethod
    def read_file(self, file_path: str, file_name: str) -> str: ...


class LocalStorage(StorageBackend):
    def store_file(self, file_path: str, file_name: str, contents: str) -> None:
        full_file_path = pathlib.Path(file_path) / file_name
        with open(full_file_path, "w") as f:
            f.write(contents)

    def read_file(self, file_path: str, file_name: str) -> str:
        full_file_path = pathlib.Path(file_path) / file_name
        with open(full_file_path) as f:
            return f.read()


def get_storage_backend() -> StorageBackend:
    return settings_base.get_class_from_string(settings_base.settings.STORAGE_BACKEND)()
