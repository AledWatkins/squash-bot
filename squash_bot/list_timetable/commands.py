import datetime
import enum
import itertools
import typing

from common.timetable import timetable
from squash_bot.core import command as _command
from squash_bot.core import command_registry, response_message
from squash_bot.core.data import constants as core_constants
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
            description="The amount of days to check for squash sessions. Default=7",
            type=core_constants.CommandOptionType.INTEGER,
            required=False,
            default=7,
        ),
        _command.CommandOption(
            name=ListTimetableOptionType.TIME_OF_DAY.value,
            description=f"The specified time of day to filter specific squash sessions. Default={timetable.TimeOfDayType.POST_WORK_SESH.value}",
            type=core_constants.CommandOptionType.STRING,
            default=timetable.TimeOfDayType.POST_WORK_SESH.value,
            required=False,
            choices=tuple(
                _command.CommandOptionChoice(
                    time_of_day.value,
                    time_of_day.value,
                    core_constants.CommandOptionType.STRING,
                )
                for time_of_day in timetable.TimeOfDayType
            ),
        ),
    )
    _timetable = timetable.CelticLeisureTimetable()

    def _handle(
        self,
        options: dict[str, typing.Any],
        base_context: dict[str, typing.Any],
        guild: core_dataclasses.Guild,
        user: core_dataclasses.User,
    ) -> response_message.ResponseBody:
        # From today's date
        from_date = datetime.datetime.now()

        # Check days is valid
        try:
            days = int(options["days"])
        except ValueError as e:
            raise _command.CommandVerificationError(
                f"Don't be daft now.. {options['days']} must be an integer"
            ) from e

        if days < 1:
            raise _command.CommandVerificationError(f"Don't be daft now.. {days} must be > 0")

        # Check time of day is valid
        try:
            time_of_day = timetable.TimeOfDayType(
                options[ListTimetableOptionType.TIME_OF_DAY.value]
            )
        except ValueError as e:
            raise _command.CommandVerificationError("Invalid time of day") from e

        to_date = from_date + datetime.timedelta(days=days)

        from_date_str = from_date.strftime(DISCORD_COMMAND_DATETIME_FORMAT)
        to_date_str = to_date.strftime(DISCORD_COMMAND_DATETIME_FORMAT)

        # Get the available sessions
        timetable_sessions = self._timetable.get_sessions(from_date, to_date)
        filtered_timetable_sessions = self._timetable.filter_sessions(
            timetable_sessions, time_of_day, show_unavailable_slots=False
        )

        # return early if no available sessions
        if not filtered_timetable_sessions:
            message = "No available sessions"
            if days == 1:
                message += f" on {from_date_str}"
            else:
                message += f" between {from_date_str} and {to_date_str}"
            return response_message.ChannelMessageResponseBody(content=message)

        content = self._get_response_message(filtered_timetable_sessions)
        return response_message.ChannelMessageResponseBody(content=content)

    @staticmethod
    def _get_response_message(sessions: list[timetable.TimetableSession]) -> str:
        session_groups = itertools.groupby(sessions, key=lambda s: s.start_datetime.date())

        session_dates = []
        for session_date, grouped_sessions in session_groups:
            pretty_date = session_date.strftime("%A (%d-%m)")
            session_str = ", ".join(str(session) for session in grouped_sessions)
            session_dates.append(f"{pretty_date}:\n\t{session_str}")

        return "\n\n".join(session_dates)
