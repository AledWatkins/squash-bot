import typing

from squash_bot.core import command as _command, command_registry, response


@command_registry.registry.register
class RecordMatchCommand(_command.Command):
    name = "record-match"
    description = "Record a match between two players"
    options = [
        _command.CommandOption(
            name="winner",
            description="The winner",
            type=_command.CommandOptionType.USER,
            required=True,
        ),
        _command.CommandOption(
            name="winner-score",
            description="The score of the winner",
            type=_command.CommandOptionType.INTEGER,
            required=True,
        ),
        _command.CommandOption(
            name="loser",
            description="The loser",
            type=_command.CommandOptionType.USER,
            required=True,
        ),
        _command.CommandOption(
            name="loser-score",
            description="The score of the loser",
            type=_command.CommandOptionType.INTEGER,
            required=True,
        ),
    ]

    def _handle(
        self, options: dict[str, typing.Any], base_context: dict[str, typing.Any]
    ) -> response.Response:
        return response.Response(
            status_code=200,
            body_data={
                "content": f"Match recorded: {options['winner']} {options['winner-score']} - {options['loser-score']} {options['loser']}"
            },
        )
