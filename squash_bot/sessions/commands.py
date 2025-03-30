import datetime
import logging
import typing

import dateparser

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
        at = dateparser.parse(
            options["when"],
            languages=["en"],
            settings={"PREFER_DATES_FROM": "future", "TIMEZONE": "Europe/London"},
        )
        if not at:
            return response_message.EphemeralChannelMessageResponseBody(
                content="Could not parse date, please reword and try again"
            )
        if at < datetime.datetime.now():
            return response_message.EphemeralChannelMessageResponseBody(
                content="Parsed date is in the past, please reword and try again"
            )

        session = operations.record_session_at(at=at, guild=guild, booked_by=user)
        session_start_string = session.start_datetime.strftime("%A %-I%p")
        return response_message.ChannelMessageResponseBody(
            content=f"Booked @ {session_start_string}"
        )
