import typing

from slash_command_register import outputer
from squash_bot.core import command as _command
from squash_bot.core import command_registry
from squash_bot.settings import base as settings_base


def register_commands() -> None:
    commands_in_registry = command_registry.all_commands()

    APP_ID = settings_base.settings.APP_ID
    SERVER_ID = settings_base.settings.SERVER_ID
    BOT_TOKEN = settings_base.settings.BOT_TOKEN

    url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{SERVER_ID}/commands"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    json = [_build_dict_for_command(command) for command in commands_in_registry]

    outputer = _outputer_from_settings()
    outputer.send({"url": url, "headers": headers, "json": json})


def _build_dict_for_command(command: _command.Command) -> dict[str, typing.Any]:
    return {
        "name": command.name,
        "description": command.description,
        "options": [_build_dict_for_option(option) for option in command.options],
    }


def _build_dict_for_option(
    command_option: _command.CommandOption,
) -> dict[str, typing.Any]:
    return {
        "name": command_option.name,
        "description": command_option.description,
        "type": command_option.type.value,
        "required": command_option.required,
        "choices": [
            choice.as_dict()
            for choice in command_option.choices
            if choice.type is command_option.type
        ],
    }


def _outputer_from_settings() -> outputer.Outputer:
    outputer_class = settings_base.settings.OUTPUTER
    return settings_base.get_class_from_string(outputer_class)()
