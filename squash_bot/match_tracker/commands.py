import datetime
import logging
import typing

from squash_bot.core import command as _command
from squash_bot.core.data import constants as core_constants
from squash_bot.core import command_registry, response_message
from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker import filterers, formatters, orderers, queries, utils, validate
from squash_bot.match_tracker.data import dataclasses, storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@command_registry.registry.register
class RecordMatchCommand(_command.Command):
    name = "record-match"
    description = "Record a match between two players. The first player is assumed to have served."
    options = (
        _command.CommandOption(
            name="player-one",
            description="Player one",
            type=core_constants.CommandOptionType.USER,
            required=True,
        ),
        _command.CommandOption(
            name="player-one-score",
            description="Player one's score",
            type=core_constants.CommandOptionType.INTEGER,
            required=True,
        ),
        _command.CommandOption(
            name="player-two",
            description="Player two",
            type=core_constants.CommandOptionType.USER,
            required=True,
        ),
        _command.CommandOption(
            name="player-two-score",
            description="Player two's score",
            type=core_constants.CommandOptionType.INTEGER,
            required=True,
        ),
    )

    def _handle(
        self,
        options: dict[str, typing.Any],
        base_context: dict[str, typing.Any],
        guild: core_dataclasses.Guild,
        user: core_dataclasses.User,
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
            # We currently assume that the first player is the one who served
            served=options["player-one"],
            # We currently don't distinguish between the time the match was played and the time it was logged
            played_at=datetime.datetime.now(),
            logged_at=datetime.datetime.now(),
            logged_by=user,
        )

        # Validate the match result
        validate.validate_match_result(match_result)

        logger.info(f"Recording match: {match_result}")
        storage.store_match_result(match_result, guild)

        return response_message.ChannelMessageResponseBody(utils.build_match_string(match_result)).as_dict()


class FilterOrderFormatMatchesMixin:
    filterer: type[filterers.Filterer] = filterers.NoopFilterer
    orderer: type[orderers.Orderer] = orderers.NoopOrderer
    formatter: type[formatters.Formatter] = formatters.BasicFormatter

    def _handle(
        self,
        options: dict[str, typing.Any],
        base_context: dict[str, typing.Any],
        guild: core_dataclasses.Guild,
        user: core_dataclasses.User,
    ) -> dict[str, typing.Any]:
        matches = queries.get_matches(guild)

        filtered_matches = self.filterer.filter(matches, **options)
        ordered_matches = self.orderer.order(filtered_matches, **options)

        if ordered_matches:
            content = self.formatter.format_matches(ordered_matches, **options)
        else:
            content = "No matches have been recorded."

        return response_message.ChannelMessageResponseBody(content).as_dict()


@command_registry.registry.register
class ShowMatchesCommand(_command.Command):
    name = "show-matches"
    description = "Show saved matches."
    options = (
        _command.CommandOption(
            name="sort-by",
            description="The field to sort the matches by. Defaults to `played_at`.",
            type=core_constants.CommandOptionType.STRING,
            required=False,
            default="played_at",
        ),
    )

    def _handle(
        self,
        options: dict[str, typing.Any],
        base_context: dict[str, typing.Any],
        guild: core_dataclasses.Guild,
        user: core_dataclasses.User,
    ) -> dict[str, typing.Any]:
        matches = queries.get_matches(guild)

        sort_by = options["sort-by"]
        matches = matches.sort_by(sort_by)

        if matches:
            content = formatters.PlayedAtFormatter.format_matches(matches)
        else:
            content = "No matches have been recorded."

        return response_message.ChannelMessageResponseBody(content).as_dict()


@command_registry.registry.register
class LeagueTableCommand(FilterOrderFormatMatchesMixin, _command.Command):
    name = "league-table"
    description = "Show league table."
    options = (
        _command.CommandOption(
            name="include-matches-from",
            description="Only include matches played on or after this date. Defaults to all time.",
            type=core_constants.CommandOptionType.STRING,
            required=False,
        ),
    )

    filterer = filterers.OptionalFromDateFilterer
    formatter = formatters.LeagueTable
