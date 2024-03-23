import typing

import attrs

from squash_bot.core import command as _command, command_registry, response


@attrs.frozen
class RecordMatchContext:
    winner: str
    winner_score: int
    loser: str
    loser_score: int


class WinnerOption(_command.CommandOption):
    name = "winner"
    description = "The name of the winner"
    type = _command.CommandOptionType.USER
    required = True


class WinnerScoreOption(_command.CommandOption):
    name = "winner_score"
    description = "The score of the winner"
    type = _command.CommandOptionType.INTEGER
    required = True


class LoserOption(_command.CommandOption):
    name = "loser"
    description = "The name of the loser"
    type = _command.CommandOptionType.USER
    required = True


class LoserScoreOption(_command.CommandOption):
    name = "loser_score"
    description = "The score of the loser"
    type = _command.CommandOptionType.INTEGER
    required = True


@command_registry.registry.register
class RecordMatchCommand(_command.Command[RecordMatchContext]):
    name = "record-match"
    description = "Record a match between two players"
    options = [
        WinnerOption(),
        WinnerScoreOption(),
        LoserOption(),
        LoserScoreOption(),
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
        pass
