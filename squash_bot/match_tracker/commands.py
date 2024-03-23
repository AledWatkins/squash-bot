import typing

import attrs

from squash_bot.core import command as _command, command_registry, response


@attrs.frozen
class RecordMatchContext:
    winner: str
    winner_score: int
    loser: str
    loser_score: int


@command_registry.registry.register
class RecordMatchCommand(_command.Command[RecordMatchContext]):
    name = "record-match"
    description = "Record a match between two players"
    options = [
        _command.CommandOption(
            name="winner",
            description="The name of the winner",
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
            description="The name of the losers",
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

    def parse_arguments(
        self, base_context: dict[str, typing.Any]
    ) -> RecordMatchContext:
        return RecordMatchContext(
            winner="Test1",
            winner_score=11,
            loser="Test2",
            loser_score=2,
        )

    def _handle(self, context: RecordMatchContext) -> response.Response:
        return response.Response(
            status_code=200,
            body_data={
                "content": f"Match recorded: {context.winner} {context.winner_score} - {context.loser_score} {context.loser}"
            },
        )
