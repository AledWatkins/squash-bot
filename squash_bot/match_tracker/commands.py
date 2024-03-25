import typing

import attrs

from squash_bot.core import command as _command
from squash_bot.core import command_registry, lambda_function


@attrs.frozen
class MatchResult:
    winner: dict[str, typing.Any]
    winner_score: int
    loser_score: int
    loser: dict[str, typing.Any]


@command_registry.registry.register
class RecordMatchCommand(_command.Command):
    name = "record-match"
    description = "Record a match between two players"
    options = (
        _command.CommandOption(
            name="player-one",
            description="Player one",
            type=_command.CommandOptionType.USER,
            required=True,
        ),
        _command.CommandOption(
            name="player-one-score",
            description="Player one's score",
            type=_command.CommandOptionType.INTEGER,
            required=True,
        ),
        _command.CommandOption(
            name="player-two",
            description="Player two",
            type=_command.CommandOptionType.USER,
            required=True,
        ),
        _command.CommandOption(
            name="player-two-score",
            description="Player two's score",
            type=_command.CommandOptionType.INTEGER,
            required=True,
        ),
    )

    def _handle(
        self, options: dict[str, typing.Any], base_context: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:
        loser, winner = sorted(
            [
                (options["player-one"], options["player-one-score"]),
                (options["player-two"], options["player-two-score"]),
            ],
            key=lambda x: x[1],
        )
        match_result = MatchResult(
            winner=winner[0], winner_score=winner[1], loser_score=loser[1], loser=loser[0]
        )

        return {
            "type": lambda_function.InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            "data": {
                "content": f"Match recorded: {match_result.winner.global_name} {match_result.winner_score} - {match_result.loser_score} {match_result.loser.global_name}"
            },
        }
