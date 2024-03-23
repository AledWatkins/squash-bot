import attrs
import typing

from squash_bot.core import response

T_command_context = typing.TypeVar("T_command_context", bound=attrs.AttrsInstance)


class CommandOption:
    name: str
    description: str
    type: str
    required: bool


class Command(typing.Generic[T_command_context]):
    name: str
    description: str
    options: list[CommandOption]

    def __init__(self) -> None: ...

    def parse_arguments(self, base_context: dict[str, typing.Any]) -> T_command_context:
        raise NotImplementedError

    def handle(self, base_context: dict[str, typing.Any]) -> response.Response:
        command_context = self.parse_arguments(base_context)
        return self._handle(command_context)

    def _handle(self, context: T_command_context) -> response.Response:
        raise NotImplementedError
