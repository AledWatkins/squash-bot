import enum
import typing

import attrs


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

    @property
    def is_user(self) -> bool:
        return self.type == CommandOptionType.USER


class Command:
    name: str
    description: str
    options: tuple[CommandOption]

    def parse_options(self, base_context: dict[str, typing.Any]) -> dict[str, typing.Any]:
        data = base_context["data"]
        options = data.get("options", [])
        provided_options = {option["name"] for option in options}
        required_options = {option.name for option in self.options if option.required}
        command_options_by_name = {option.name: option for option in self.options}

        if missing_required_options := required_options - provided_options:
            raise CommandVerificationError(
                f"Missing required options: {','.join(missing_required_options)}"
            )

        return_options = {}
        for option in options:
            option_name = option["name"]
            command_option = command_options_by_name[option_name]

            if command_option.is_user:
                user_data = data.get("resolved", {}).get("users", {}).get(option["value"], None)
                value = data.User(
                    id=user_data["id"],
                    username=user_data["username"],
                    global_name=user_data["global_name"],
                )
            else:
                value = option["value"]

            return_options[option_name] = value

        return return_options

    def handle(self, base_context: dict[str, typing.Any]) -> dict[str, typing.Any]:
        command_options = self.parse_options(base_context)
        return self._handle(options=command_options, base_context=base_context)

    def _handle(
        self, options: dict[str, typing.Any], base_context: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:
        raise NotImplementedError
