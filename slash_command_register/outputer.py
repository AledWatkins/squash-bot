import logging
import typing

import requests
import tabulate

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Outputer:
    def send(self, data: dict[str, typing.Any]) -> None:
        raise NotImplementedError


class PrintOutputer(Outputer):
    def send(self, data: dict[str, typing.Any]) -> None:
        commands_data = data["json"]
        command_list = []
        for command_data in commands_data:
            command_options_str = ", ".join(
                f"{option['name']}{'*' if option['required'] else ''}"
                for option in command_data["options"]
            )
            command_list.append([command_data["name"], command_options_str])

        print(tabulate.tabulate(command_list, headers=["Command", "Options"], tablefmt="simple"))  # noqa: T201


class RequestsOutputer(Outputer):
    def send(self, data: dict[str, typing.Any]) -> None:
        response = requests.put(data["url"], headers=data["headers"], json=data["json"])
        print(response.status_code)  # noqa: T201
