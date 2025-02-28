import pytest

from squash_bot.core import command as _command
from squash_bot.core.data import constants as core_constants
from squash_bot.core.data import dataclasses as core_dataclasses


class TestParseOptions:
    def test_throws_error_for_missing_required_option(self):
        class TestCommand(_command.Command):
            name = "test-command"
            description = "Test command"
            options = (
                _command.CommandOption(
                    name="required-option",
                    description="A required option",
                    type=core_constants.CommandOptionType.STRING,
                    required=True,
                ),
            )

        command = TestCommand()
        with pytest.raises(
            _command.CommandVerificationError,
            match="Missing required options: required-option",
        ):
            command.parse_options({"data": {"options": []}})

    def test_options_passed_to_handle(self):
        class TestCommand(_command.Command):
            name = "test-command"
            description = "Test command"
            options = (
                _command.CommandOption(
                    name="required-option",
                    description="A required option",
                    type=core_constants.CommandOptionType.STRING,
                    required=True,
                ),
            )

            def _handle(self, options, base_context, guild, user):
                return options

        assert TestCommand().handle(
            {
                "data": {
                    "options": [{"name": "required-option", "value": "value"}],
                    "guild_id": "1",
                },
                "member": {
                    "user": {
                        "id": "1",
                        "username": "different-name",
                        "global_name": "different-global-name",
                    }
                },
            }
        ) == {"required-option": "value"}

    def test_user_options_include_username(self):
        class TestCommand(_command.Command):
            name = "test-command"
            description = "Test command"
            options = (
                _command.CommandOption(
                    name="user",
                    description="User",
                    type=core_constants.CommandOptionType.USER,
                    required=True,
                ),
            )

            def _handle(self, options, base_context, guild, user):
                return options

        assert TestCommand().handle(
            {
                "data": {
                    "options": [
                        {"name": "user", "type": 6, "value": "1"},
                    ],
                    "resolved": {
                        "users": {
                            "1": {
                                "id": "1",
                                "username": "name",
                                "global_name": "global-name",
                            }
                        }
                    },
                    "guild_id": "1",
                },
                "member": {
                    "user": {
                        "id": "1",
                        "username": "different-name",
                        "global_name": "different-global-name",
                    }
                },
            }
        ) == {"user": core_dataclasses.User(id="1", username="name", global_name="global-name")}

    def test_default(self):
        class TestCommand(_command.Command):
            name = "test-command"
            description = "Test command"
            options = (
                _command.CommandOption(
                    name="required-option",
                    description="A required option",
                    type=core_constants.CommandOptionType.STRING,
                    required=False,
                    default="default-value",
                ),
            )

        command = TestCommand()
        assert command.parse_options(
            {"data": {"options": [{"name": "required-option", "value": ""}]}}
        ) == {"required-option": "default-value"}

    def test_default_when_option_not_in_data(self):
        class TestCommand(_command.Command):
            name = "test-command"
            description = "Test command"
            options = (
                _command.CommandOption(
                    name="required-option",
                    description="A required option",
                    type=core_constants.CommandOptionType.STRING,
                    required=False,
                    default="default-value",
                ),
            )

        command = TestCommand()
        assert command.parse_options({"data": {"options": []}}) == {
            "required-option": "default-value"
        }


class TestParseGuild:
    def test_guild(self):
        class TestCommand(_command.Command):
            name = "test-command"
            description = "Test command"
            options = ()

            def _handle(self, options, base_context, guild, user):
                return guild

        assert TestCommand().handle(
            {
                "data": {"guild_id": "1"},
                "member": {
                    "user": {
                        "id": "1",
                        "username": "different-name",
                        "global_name": "different-global-name",
                    }
                },
            }
        ) == core_dataclasses.Guild(guild_id="1")


class TestParseUser:
    def test_user(self):
        class TestCommand(_command.Command):
            name = "test-command"
            description = "Test command"
            options = ()

            def _handle(self, options, base_context, guild, user):
                return user

        assert TestCommand().handle(
            {
                "data": {
                    "options": [],
                    "guild_id": "1",
                },
                "member": {
                    "user": {
                        "id": "1",
                        "username": "different-name",
                        "global_name": "different-global-name",
                    }
                },
            }
        ) == core_dataclasses.User(
            id="1", username="different-name", global_name="different-global-name"
        )
