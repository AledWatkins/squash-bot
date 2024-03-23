import attrs
import typing

T_command_context = typing.TypeVar("T_command_context", bound=attrs.AttrsInstance)


class Command(typing.Generic[T_command_context]):
    name: str

    def __init__(self) -> None: ...

    def parse_arguments(self, base_context: dict[str, typing.Any]) -> T_command_context:
        raise NotImplementedError

    def handle(self, base_context: dict[str, typing.Any]) -> None:
        command_context = self.parse_arguments(base_context)
        return self._handle(command_context)

    def _handle(self, context: T_command_context) -> None:
        raise NotImplementedError
