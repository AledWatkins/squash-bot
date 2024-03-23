import pytest

from squash_bot.core import command_registry
from squash_bot.core import command as _command


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
