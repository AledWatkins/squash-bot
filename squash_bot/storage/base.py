import abc
import io
import logging
import pathlib

import boto3
from botocore import exceptions as botocore_exceptions

from squash_bot.settings import base as settings_base

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FileMissing(Exception):
    """
    Raised when a file is not found
    """


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


class S3Storage(StorageBackend):
    def store_file(self, file_path: str, file_name: str, contents: str) -> None:
        bucket = self._get_bucket(file_path)
        contents_bytes = io.BytesIO(contents.encode("utf-8"))
        return bucket.upload_fileobj(contents_bytes, file_name)

    def read_file(self, file_path: str, file_name: str) -> str:
        bucket = self._get_bucket(file_path)
        try:
            return bucket.download_file(file_name, file_path)
        except botocore_exceptions.ClientError as exc:
            raise FileMissing from exc

    def _get_bucket(self, bucket_name: str):
        s3_resource = boto3.resource("s3")
        return s3_resource.Bucket(bucket_name)


def store_file(file_path: str, file_name: str, contents: str) -> None:
    logger.info(f"Storing file: {file_path} / {file_name}")
    get_storage_backend().store_file(file_path, file_name, contents)


def read_file(file_path: str, file_name: str) -> str:
    logger.info(f"Reading file: {file_path} / {file_name}")
    return get_storage_backend().read_file(file_path, file_name)


def get_storage_backend() -> StorageBackend:
    return settings_base.get_class_from_string(settings_base.settings.STORAGE_BACKEND)()
