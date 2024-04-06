import datetime
import enum
import typing

from . import timetable

from squash_bot.core import command as _command
from squash_bot.core import command_registry, lambda_function
from squash_bot.core.command import CommandVerificationError
from squash_bot.core.data import dataclasses as core_dataclasses


DISCORD_COMMAND_DATETIME_FORMAT = "%d-%m"


class ListTimetableOptionType(enum.Enum):
    DAYS = "days"
    TIME_OF_DAY = "time-of-day"


@command_registry.registry.register
class ListTimetableCommand(_command.Command):
    name = "list-timetable"
    description = "Get a list of squash timetable sessions for the coming days"
    options = (
        _command.CommandOption(
            name=ListTimetableOptionType.DAYS.value,
            description="The amount of days to check for squash sessions",
            type=_command.CommandOptionType.INTEGER,
            required=True,
        ),
        _command.CommandOption(
            name=ListTimetableOptionType.TIME_OF_DAY.value,
            description="The specified time of day to filter specific squash sessions. Default = Any",
            type=_command.CommandOptionType.STRING,
            default=timetable.TimeOfDayType.ANY.value,
            required=False,
        ),
    )
    _timetable = timetable.CelticLeisureTimetable()

    def _handle(
        self,
        options: dict[str, typing.Any],
        base_context: dict[str, typing.Any],
        guild: core_dataclasses.Guild,
        user: core_dataclasses.User,
    ) -> dict[str, typing.Any]:
        # From today's date
        from_date = datetime.datetime.now()

        # Check days is valid
        try:
            days = int(options["days"])
        except ValueError:
            raise CommandVerificationError(
                f"Don't be daft now.. {options['days']} must be an integer"
            )

        if days < 1:
            raise CommandVerificationError(f"Don't be daft now.. {days} must be > 0")

        # Check time of day - as it is not required (or could be invalid), default to ANY
        try:
            time_of_day = timetable.TimeOfDayType[
                options[ListTimetableOptionType.TIME_OF_DAY.value].upper()
            ]
        except KeyError:
            raise CommandVerificationError("Invalid time of day")

        to_date = from_date + datetime.timedelta(days=days)

        from_date_str = from_date.strftime(DISCORD_COMMAND_DATETIME_FORMAT)
        to_date_str = to_date.strftime(DISCORD_COMMAND_DATETIME_FORMAT)

        # Get the available sessions
        timetable_sessions = self._timetable.get_sessions(from_date, to_date)
        filtered_timetable_sessions = self._timetable.filter_sessions(
            timetable_sessions, time_of_day, False
        )

        # return early if no available sessions
        if not filtered_timetable_sessions:
            message = "No available sessions"
            if days == 1:
                message += f" on {from_date_str}"
            else:
                message += f" between {from_date_str} and {to_date_str}"

            return {
                "content": message,
                "type": lambda_function.InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            }

        # Store the time period (default is 'from_date' if only 1 day requested) for the response message header
        time_period_str = from_date_str
        if days > 1:
            time_period_str += f" - {to_date_str}"

        return {
            "content": self._get_response_message(
                filtered_timetable_sessions, f"{time_of_day.value} slots ({time_period_str})"
            ),
            "type": lambda_function.InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
        }

    def _get_response_message(
        self, sessions: list[timetable.TimetableSession], header: str
    ) -> str:
        message = f"{header}:\n"
        message += "\n".join(
            f"* [{session}]({self._timetable.get_booking_link(session.schedule_id)})"
            for session in sessions
        )

        return message
