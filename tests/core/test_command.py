import pytest

from squash_bot.core import command as _command


class TestParseOptions:
    def test_throws_error_for_missing_required_option(self):
        class TestCommand(_command.Command):
            name = "test-command"
            description = "Test command"
            options = (
                _command.CommandOption(
                    name="required-option",
                    description="A required option",
                    type=_command.CommandOptionType.STRING,
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
                    type=_command.CommandOptionType.STRING,
                    required=True,
                ),
            )

            def _handle(self, options, base_context):
                return options

        assert TestCommand().handle(
            {"data": {"options": [{"name": "required-option", "value": "value"}]}}
        ) == {"required-option": "value"}
