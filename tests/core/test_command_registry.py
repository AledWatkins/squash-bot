from unittest import mock

import pytest

from squash_bot.core import command as _command
from squash_bot.core import command_registry


class TestRegistry:
    def test_register(self):
        registry = command_registry.Registry()

        @registry.register
        class TestCommand(_command.Command):
            name = "test"

        assert "test" in registry.commands.keys()

    def test_throws_error_on_duplicate_command_name(self):
        registry = command_registry.Registry()

        @registry.register
        class TestCommandOne(_command.Command):
            name = "test"

        with pytest.raises(command_registry.ImproperlyConfigured):

            @registry.register
            class TestCommandTwo(_command.Command):
                name = "test"


class TestAllCommands:
    @mock.patch("squash_bot.core.command_registry.registry")
    def test_returns_all_commands(self, mock_registry):
        class TestCommandOne(_command.Command):
            name = "test-one"

        class TestCommandTwo(_command.Command):
            name = "test-two"

        mock_registry.commands = {
            "test-one": TestCommandOne(),
            "test-two": TestCommandTwo(),
        }

        all_commands = command_registry.all_commands()
        assert len(all_commands) == 2

        command_names = sorted([command.name for command in all_commands])
        assert command_names == ["test-one", "test-two"]


class TestRegisteredCommands:
    def test_command_choices_are_correct_type(self):
        """
        All `choices` on command options must have the same type as the option itself
        """
        commands = command_registry.all_commands()

        for command in commands:
            for option in command.options:
                if not option.choices:
                    continue

                assert all(choice.type == option.type for choice in option.choices)
