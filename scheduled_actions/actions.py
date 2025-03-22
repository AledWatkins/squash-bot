import abc
import datetime
import logging
from collections.abc import Iterable

from common.settings import base as settings_base
from common.timetable import timetable
from scheduled_actions import dataclasses, send

logger = logging.getLogger("scheduled_actions.actions")
logger.setLevel(logging.INFO)


class Action(abc.ABC):
    code: str

    @abc.abstractmethod
    def run(self, context: dict) -> None: ...


class PromptSessionBooking(Action):
    code = "prompt-session-booking"

    def run(self, context: dict) -> None:
        sessions = self._get_sessions()
        message = dataclasses.Message(
            content=self._build_message_content(sessions),
        )
        for channel in self._channels_to_notify():
            logger.info(f"{self.__class__.__name__} - Sending message to channel {channel.id}")
            send.send_message_to_channel(channel=channel, message=message)

    def _channels_to_notify(self) -> Iterable[dataclasses.Channel]:
        yield from [
            dataclasses.Channel(
                id=channel_id,
            )
            for channel_id in settings_base.settings.PROMPT_SESSION_BOOKING_CHANNEL_IDS
        ]

    def _get_sessions(self) -> list[timetable.TimetableSession]:
        sessions = timetable.CelticLeisureTimetable().get_sessions(
            from_date=datetime.datetime.now(),
            to_date=datetime.datetime.now() + datetime.timedelta(days=7),
        )
        logger.info(f"{self.__class__.__name__} - Got {len(sessions)} sessions from API")

        # We only want to notify about sessions at 6pm on weekdays
        time_of_day = [18]
        days = timetable.DayType.WEEKDAY
        return timetable.CelticLeisureTimetable.filter_sessions(sessions, time_of_day, days=days)

    def _build_message_content(self, sessions: list[timetable.TimetableSession]) -> str:
        base_msg = "Are we playing squash this week?"

        week_days = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        available_week_days = [week_days[session.start_datetime.weekday()] for session in sessions]
        if not available_week_days:
            return base_msg + " All 6pm sessions are already booked this week 💀"
        elif len(available_week_days) > 3:
            non_available_days = set(week_days.values()) - set(available_week_days)
            return (
                base_msg + f" 6pm is free every day other than {' and '.join(non_available_days)}"
            )
        else:
            return (
                base_msg
                + f" 6pm is free on {', '.join(available_week_days[:-1]) + ' and ' + available_week_days[-1]}"
            )


actions = [
    PromptSessionBooking(),
]
