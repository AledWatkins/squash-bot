import logging
import typing

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Outputer:
    def send(self, data: dict[str, typing.Any]) -> None:
        raise NotImplementedError


class PrintOutputer(Outputer):
    def send(self, data: dict[str, typing.Any]) -> None:
        print(data)  # noqa: T201


class RequestsOutputer(Outputer):
    def send(self, data: dict[str, typing.Any]) -> None:
        response = requests.put(data["url"], headers=data["headers"], json=data["json"])
        print(response.status_code)  # noqa: T201
