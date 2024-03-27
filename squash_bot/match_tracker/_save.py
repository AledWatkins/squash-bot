import io
import json
import typing
from abc import ABC, abstractmethod

import attrs

from squash_bot.settings import base as settings_base

from .commands import MatchResult


@attrs.frozen
class Results:
    results: list[MatchResult]

    @classmethod
    def from_dict(cls, data) -> "Results":
        return cls(results=[MatchResult.from_dict(result) for result in data])

    def as_dict(self) -> dict[str, typing.Any]:
        return [result.as_dict() for result in self.results]

    def add_result(self, result: MatchResult) -> None:
        self.results.append(result)


class Storage(ABC):
    @abstractmethod
    def write(self): ...


class LocalStorage(Storage):
    def write(self, file: io.StringIO, data: dict[str, typing.Any]):
        json.dump(data, file, indent=4)


class S3Storage(Storage):
    def write(self, file: io.StringIO, data: dict[str, typing.Any]):
        # TODO:
        pass


def save_results(results: Results):
    storage_class = _storage_from_settings()
    storage_class.write(results.as_dict())


def _storage_from_settings() -> Storage:
    storage_class = settings_base.settings.STORAGE
    return settings_base.get_class_from_string(storage_class)()
