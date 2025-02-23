import abc
import io
import logging
import pathlib

import boto3
from botocore import exceptions as botocore_exceptions

from common.settings import base as settings_base

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


client = boto3.client("s3")


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
        full_file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(full_file_path, "w") as f:
            f.write(contents)

    def read_file(self, file_path: str, file_name: str) -> str:
        full_file_path = pathlib.Path(file_path) / file_name
        with open(full_file_path) as f:
            return f.read()


class S3Storage(StorageBackend):
    def store_file(self, file_path: str, file_name: str, contents: str) -> None:
        client = self._client()
        contents_bytes = io.BytesIO(contents.encode("utf-8"))
        return client.put_object(Key=file_name, Bucket=file_path, Body=contents_bytes)

    def read_file(self, file_path: str, file_name: str) -> str:
        client = self._client()
        try:
            response = client.get_object(Bucket=file_path, Key=file_name)
        except botocore_exceptions.ClientError as exc:
            raise FileMissing from exc
        return response["Body"].read().decode("utf-8")

    def _client(self):
        return client


def store_file(file_path: str, file_name: str, contents: str) -> None:
    logger.info(f"Storing file: {file_path} / {file_name}")
    get_storage_backend().store_file(file_path, file_name, contents)


def read_file(
    file_path: str,
    file_name: str,
    create_if_missing: bool = False,
) -> str:
    logger.info(f"Reading file: {file_path} / {file_name}")
    storage_backend = get_storage_backend()
    try:
        return storage_backend.read_file(file_path, file_name)
    except FileMissing:
        if create_if_missing:
            logger.info("File not found, creating")
            storage_backend.store_file(file_path, file_name, "")
            return ""
        else:
            raise


def get_storage_backend() -> StorageBackend:
    return settings_base.get_class_from_string(  # type: ignore[abstract]
        settings_base.settings.STORAGE_BACKEND, StorageBackend
    )()
