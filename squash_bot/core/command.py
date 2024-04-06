import typing

import attrs

from squash_bot.core.data import constants as core_constants
from squash_bot.core.data import dataclasses as core_dataclasses


class CommandError(Exception):
    """
    Base class for command errors
    """


class CommandVerificationError(CommandError):
    """
    Error raised when a command fails verification
    """


@attrs.frozen
class CommandOptionChoice:
    """
    A predetermined choice for a command option.
    Note: type MUST match the CommandOption.type otherwise the choices will fail to be included
    """

    name: str
    value: str | int | float
    type: core_constants.CommandOptionType

    def as_dict(self) -> dict[str, str | int | float]:
        return {"name": self.name, "value": self.value}


@attrs.frozen
class CommandOption:
    name: str
    description: str
    type: core_constants.CommandOptionType
    required: bool
    default: typing.Any | None = None
    choices: tuple[CommandOptionChoice, ...] | None = None

    @property
    def is_user(self) -> bool:
        return self.type == core_constants.CommandOptionType.USER


class Command:
    name: str
    description: str
    options: tuple[CommandOption]

    def parse_options(self, base_context: dict[str, typing.Any]) -> dict[str, typing.Any]:
        data = base_context["data"]
        options = data.get("options", [])
        provided_options = {option["name"] for option in options}
        required_options = {option.name for option in self.options if option.required}
        options_with_default = {option.name for option in self.options if option.default}
        command_options_by_name = {option.name: option for option in self.options}

        if missing_required_options := required_options - provided_options:
            raise CommandVerificationError(
                f"Missing required options: {','.join(missing_required_options)}"
            )

        return_options: dict[str, typing.Any] = {}
        for option in options:
            option_name = option["name"]
            command_option = command_options_by_name[option_name]

            if command_option.is_user:
                user_data = data.get("resolved", {}).get("users", {}).get(option["value"], None)
                value = core_dataclasses.User(
                    id=user_data["id"],
                    username=user_data["username"],
                    global_name=user_data["global_name"],
                )
            else:
                value = option["value"]

            if not value and command_option.default:
                value = command_option.default

            return_options[option_name] = value

        for option_name in options_with_default - provided_options:
            command_option = command_options_by_name[option_name]
            return_options[option_name] = command_option.default

        return return_options

    def parse_guild(self, base_context: dict[str, typing.Any]) -> core_dataclasses.Guild:
        guild_id = base_context["data"]["guild_id"]
        return core_dataclasses.Guild(guild_id=guild_id)

    def parse_user(self, base_context: dict[str, typing.Any]) -> core_dataclasses.User:
        user_data = base_context["member"]["user"]
        return core_dataclasses.User(
            id=user_data["id"],
            username=user_data["username"],
            global_name=user_data["global_name"],
        )

    def handle(self, base_context: dict[str, typing.Any]) -> dict[str, typing.Any]:
        command_options = self.parse_options(base_context)
        guild = self.parse_guild(base_context)
        user = self.parse_user(base_context)
        return self._handle(
            options=command_options, base_context=base_context, guild=guild, user=user
        )

    def _handle(
        self,
        options: dict[str, typing.Any],
        base_context: dict[str, typing.Any],
        guild: core_dataclasses.Guild,
        user: core_dataclasses.User,
    ) -> dict[str, typing.Any]:
        """
        Should be implemented by subclasses to handle the command.

        :param options: The parsed options, provided as a dictionary keyed by option name
        :param base_context: The base context provided by the Discord API
        :param guild: A `Guild` dataclass representing guild the command was executed in
        :param user: A `User` dataclass representing the user who executed the command
        :return: A dictionary representing the response to the command
        """
        raise NotImplementedError
