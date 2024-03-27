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
        logger.info(f"Outputer: {data}")


class RequestsOutputer(Outputer):
    def send(self, data: dict[str, typing.Any]) -> None:
        requests.put(data["url"], headers=data["headers"], json=data["json"])
