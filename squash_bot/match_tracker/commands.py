import typing
from datetime import datetime

import attrs

from squash_bot.core import command as _command
from squash_bot.core import command_registry, lambda_function


@attrs.frozen
class MatchResult:
    winner: dict[str, typing.Any]
    winner_score: int
    loser_score: int
    loser: dict[str, typing.Any]
    logged_at: datetime

    def as_dict(self) -> dict[str, typing.Any]:
        return {
            "winner": self.winner,
            "winner_score": self.winner_score,
            "loser_score": self.loser_score,
            "loser": self.loser,
            "logged_at": self.logged_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "MatchResult":
        return cls(
            winner=data["winner"],
            winner_score=data["winner_score"],
            loser=data["loser"],
            loser_score=data["loser_score"],
            logged_at=data["logged_at"].fromisoformat(),
        )


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
            winner=winner[0],
            winner_score=winner[1],
            loser_score=loser[1],
            loser=loser[0],
            logged_at=datetime.now(),
        )
        # TODO: Load results here and add new match result
        return {
            "type": lambda_function.InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            "data": {
                "content": f"Match recorded: {match_result.winner.global_name} {match_result.winner_score} - {match_result.loser_score} {match_result.loser.global_name}"
            },
        }
