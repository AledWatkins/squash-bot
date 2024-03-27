import datetime
import typing

from squash_bot.core import command as _command
from squash_bot.core import command_registry, lambda_function
from squash_bot.match_tracker.data import dataclasses


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
        match_result = dataclasses.MatchResult(
            winner=winner[0],
            winner_score=winner[1],
            loser_score=loser[1],
            loser=loser[0],
            # We currently don't distinguish between the time the match was played and the time it was logged
            played_at=datetime.datetime.now(),
            logged_at=datetime.datetime.now(),
        )

        return {
            "type": lambda_function.InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            "data": {
                "content": f"Match recorded: {match_result.winner.name} {match_result.winner_score} - {match_result.loser_score} {match_result.loser.name}"
            },
        }
