import datetime
import logging
import typing

from dateparser import search

from squash_bot.core import command, command_registry, response_message
from squash_bot.core.data import constants
from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.sessions import operations

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@command_registry.registry.register
class BookSession(command.Command):
    name = "book-session"
    description = "Record the time and date of a booked session"

    options = (
        command.CommandOption(
            name="when",
            description="When is the session? e.g. Monday at 6pm",
            type=constants.CommandOptionType.STRING,
            required=True,
        ),
    )

    def _handle(
        self,
        options: dict[str, typing.Any],
        base_context: dict[str, typing.Any],
        guild: core_dataclasses.Guild,
        user: core_dataclasses.User,
    ) -> response_message.ResponseBody:
        logger.info("Booking session at '%s'", options["when"])
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        logger.info("Current time is '%s'", now)
        results = search.search_dates(
            options["when"],
            languages=["en"],
            settings={
                "PREFER_DATES_FROM": "future",
                "RELATIVE_BASE": now,
                "TIMEZONE": "Europe/London",
                "RETURN_AS_TIMEZONE_AWARE": True,
                "TO_TIMEZONE": "Europe/London",
            },
        )
        if not results:
            return response_message.EphemeralChannelMessageResponseBody(
                content="Could not parse date, please reword and try again"
            )
        # `search_dates` returns a list of tuples, we only want the first one, and the first element of that tuple is
        # the datetime object
        at = results[0][1]
        logger.info("Parsed date is '%s'", at)
        if at < datetime.datetime.now(tz=at.tzinfo):
            return response_message.EphemeralChannelMessageResponseBody(
                content="Parsed date is in the past, please reword and try again"
            )

        session = operations.record_session_at(at=at, guild=guild, booked_by=user)

        logger.info("Session booked: %s", session)
        session_start_string = session.start_datetime.strftime("%A %-I%p")
        return response_message.ChannelMessageResponseBody(
            content=f"Booked @ {session_start_string}"
        )
