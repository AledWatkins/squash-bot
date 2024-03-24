import enum

import attrs
import typing


class CommandError(Exception):
    """
    Base class for command errors
    """


class CommandVerificationError(CommandError):
    """
    Error raised when a command fails verification
    """


class CommandOptionType(enum.Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


@attrs.frozen
class CommandOption:
    name: str
    description: str
    type: CommandOptionType
    required: bool


class Command:
    name: str
    description: str
    options: list[CommandOption]

    def __init__(self) -> None: ...

    def parse_options(
        self, base_context: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:
        options = base_context.get("options", [])
        provided_options = {option["name"] for option in options}
        required_options = {option.name for option in self.options if option.required}

        if missing_required_options := required_options - provided_options:
            raise CommandVerificationError(
                f"Missing required options: {','.join(missing_required_options)}"
            )

        return {option["name"]: option["value"] for option in options}

    def handle(self, base_context: dict[str, typing.Any]) -> dict[str, typing.Any]:
        command_options = self.parse_options(base_context)
        return self._handle(options=command_options, base_context=base_context)

    def _handle(
        self, options: dict[str, typing.Any], base_context: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:
        raise NotImplementedError
